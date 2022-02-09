# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""XML renderer"""

import copy
import types
import random

try:
    from cStringIO import StringIO as BufferIO
except ImportError:
    from io import BytesIO as BufferIO

try:
    from codecs import open as fileopen
except ImportError:
    fileopen = open

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from lxml import etree, objectify

CHECK_ATTRIBUTES = False

# Namespace for the ``meld:id`` attribute
MELD_NS = 'http://www.plope.com/software/meld3'
_MELD_ID = '{%s}id' % MELD_NS

# ---------------------------------------------------------------------------


class Component(object):
    def render(self, renderer):
        return self


def is_iterable(o):
    return isinstance(o, (list, tuple, types.GeneratorType))


def flatten(l, renderer):  # noqa: E741
    for e in l:
        if isinstance(e, Component):
            e = e.render(renderer)

        if is_iterable(e):
            for x in flatten(e, renderer):
                yield x
        else:
            yield e

# ---------------------------------------------------------------------------


class Tag(etree.ElementBase):
    """A xml tag
    """

    _dummy_maker = objectify.ElementMaker(annotate=False)

    def init(self, renderer):
        """Each tag keeps track of the renderer that created it

        Return:
           - ``self``
        """
        self._renderer = renderer

    @property
    def root(self):
        return self.getroottree().getroot()

    @property
    def renderer(self):
        """Return the renderer that created this tag

        Return:
          - the renderer
        """
        # The renderer is search first, in this tag, else at the root of the tree
        return getattr(self, '_renderer', None) or getattr(self.root, '_renderer', None)

    def on_change(self):
        if CHECK_ATTRIBUTES and self._authorized_attribs and not frozenset(self.attrib).issubset(self._authorized_attribs):
            raise AttributeError(
                'Bad attributes for element <%s>: ' % self.tag + ', '.join(frozenset(self.attrib) - self._authorized_attribs)
            )

    def add_children(self, children, attrib=None):
        if not children and not attrib:
            return

        dummy = self._dummy_maker.dummy(attrib, *flatten(children, self.renderer))

        if dummy.text:
            if len(self):
                self[0].tail = (self[0].tail or '') + dummy.text
            else:
                self.text = (self.text or '') + dummy.text

        self.attrib.update(dummy.attrib)
        self.extend(dummy.iterchildren())

        self.on_change()

    def __call__(self, *children, **attrib):
        """Append child and attributes to this tag

        In:
          - ``children`` -- children to add
          - ``attrib`` -- attributes to add

        Return:
          - ``self``
        """
        attrib = {
            name.replace('_', '-') if name.startswith('data_') else name.rstrip('_'): value
            for name, value in attrib.items()
        }

        self.add_children(children, attrib)

        return self

    def __enter__(self):
        self.renderer.enter(self)

        return self

    def __exit__(self, exception, data, tb):
        if exception is None:
            self.renderer.exit(self)

    def tostring(self, method='xml', encoding='utf-8', pipeline=True, **kw):
        """Serialize in XML the tree beginning at this tag

        In:
          - ``encoding`` -- encoding of the XML
          - ``pipeline`` -- if False, the ``meld:id`` attributes are deleted

        Return:
          - the XML
        """
        if not pipeline:
            for element in self.xpath('.//*[@meld:id]', namespaces={'meld': MELD_NS}):
                del element.attrib[_MELD_ID]

        return etree.tostring(self, method=method, encoding=encoding, **kw)

    def findmeld(self, id, default=None):
        """Find a tag with a given ``meld:id`` value

        In:
          - ``id`` -- value of the ``meld:id`` attribute to search
          - ``default`` -- value returned if the tag is not found

        Return:
          - the tag found, else the ``default`` value
        """
        nodes = self.xpath('.//*[@meld:id="%s"]' % id, namespaces={'meld': MELD_NS})

        # Return only the first tag found
        return nodes[0] if len(nodes) != 0 else default

    def meld_id(self, id):
        """Set the value of the attribute ``meld:id`` of this tag

        In:
          - ``id`` - value of the ``meld;id`` attribute

        Return:
          - ``self``
        """
        self.set(_MELD_ID, id)

        return self

    def fill(self, *children, **attrib):
        """Change all the child and append attributes of this tag

        In:
          - ``children`` -- list of the new children of this tag
          - ``attrib`` -- dictionnary of attributes of this tag

        Return:
          - ``self``
        """
        del self[:]
        self.text = None

        return self.__call__(*children, **attrib)

    def replace(self, *children):
        """Replace this tag by others
        In:
          - ``children`` -- list of tags to replace this tag
        """
        parent = self.getparent()

        # We can not replace the root of the tree
        if parent is not None:
            tail = self.tail
            nb_siblings = len(parent)

            i = parent.index(self)
            parent.fill(parent.text or '', parent[:i], children, self.tail or '', parent[i + 1:])

            if len(parent) >= nb_siblings:
                parent[i - nb_siblings].tail = tail

        return self

    def repeat(self, iterable, childname=None):
        """Iterate over a sequence, cloning a new child each time

        In:
          - ``iterable`` -- the sequence
          - ``childname`` -- If ``None``, clone this tag each time else
            clone each time the tag that have ``childname`` as ``meld:id`` value

        Return:
          - list of tuples (cloned child, item of the sequence)
        """
        # Find the child to clone
        element = self if childname is None else self.findmeld(childname)

        parent = element.getparent()
        parent.remove(element)

        for thing in iterable:
            clone = copy.deepcopy(element)
            clone._renderer = element.renderer
            parent.append(clone)

            yield clone, thing


class TagProp(object):
    """Tag factory with a behavior of an object attribute

    Each time this attribute is read, a new tag is created
    """
    def __init__(self, name, authorized_attribs=None, factory=None):
        """Initialization

        In:
          - ``name`` -- name of the tags to create
          - ``authorized_attribs`` -- names of the valid attributes
          - ``factory`` -- special factory to create the tag
        """
        self._name = name
        self._factory = factory

        if CHECK_ATTRIBUTES:
            self._authorized_attribs = frozenset(authorized_attribs) if authorized_attribs is not None else None

    def __get__(self, renderer, cls):
        """Create a new tag each time this attribute is read

        In:
          - ``renderer`` -- the object that has this attribute
          - ``cls`` -- *not used*

        Return:
          - a new tag
        """
        if self._factory:
            element = self._factory()
            element.tag = self._name
            element.init(renderer)
        else:
            element = renderer.makeelement(self._name)

        if CHECK_ATTRIBUTES:
            element._authorized_attribs = self._authorized_attribs

        return element

# -----------------------------------------------------------------------


class XmlRenderer(object):
    """The base class of all the renderers that generate a XML dialect
    """

    doctype = ''
    content_type = 'text/xml'

    _parser = etree.XMLParser()
    _parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=Tag))

    def __init__(self, parent=None, *args, **kw):
        """Renderer initialisation
        """
        if parent is None:
            self.namespaces = None
            self._default_namespace = None
        else:
            self.namespaces = parent.namespaces
            self._default_namespace = parent._default_namespace

        self.parent = parent
        self._prefix = ''

        # The elements tree, initialized with a dummy root
        self._children = [[]]

        # Each renderer created has a unique id
        self.id = self.generate_id('renderer_')

    def __reduce__(self):
        """Prevent a renderer to be pickled

        Prevent the common error of capturing the renderer into the closure
        of a callback
        """
        raise TypeError("can't pickle Renderer objects (are you using a renderer object in a callback ?)")

    @staticmethod
    def generate_id(prefix=''):
        """Generate a random id

        In:
          - ``prefix`` -- prefix of the generated id
        """
        return prefix + str(random.randint(10000000, 99999999))

    @staticmethod
    def comment(text=''):
        """Create a comment element

        In:
          - ``text`` -- text of the comment

        Return:
          - the new comment element
        """
        return etree.Comment(text)

    @staticmethod
    def processing_instruction(target, text=None):
        """Create a processing instruction element

        In:
          - ``target`` -- the PI target
          - ``text`` -- the PI text

        Return:
          - the new processing instruction element
        """
        return etree.PI(target, text)

    @property
    def default_namespace(self):
        """Return the default_namespace

        Return:
          - the default namespace or ``None`` if no default namespace was set
        """
        return self._default_namespace

    @default_namespace.setter
    def default_namespace(self, namespace):
        """Change the default namespace

        The namespace must be a key of the ``self.namespaces`` dictionary or be
        ``None``

        For example:

        .. code-block:: python

          x.namespaces = { 'xsl' : 'http://www.w3.org/1999/XSL/Transform' }
          x.set_default_namespace('xsl')
        """
        self._default_namespace = namespace
        self._prefix = '' if namespace is None else ('{%s}' % self.namespaces[namespace])

    @property
    def root(self):
        """Return the first tag(s) sent to the renderer

        .. warning::
            A list of tags can be returned

        Return:
          - the tag(s)
        """
        root = list(flatten(self._children[0], self))

        return root[0] if len(root) == 1 else root

    def new(self, *args, **kw):
        return self.__class__(*args, **kw)

    def makeelement(self, tag, *args):
        """Make a tag, in the default namespace set

        In:
          - ``tag`` -- name of the tag to create

        Return:
          - the new tag
        """
        # Create the tag with in the default namespace
        element = self._parser.makeelement(self._prefix + tag, nsmap=self.namespaces)
        element.init(self)

        return element

    def enter(self, current):
        """A new tag is pushed by a ``with`` statement

        In:
          - ``current`` -- the tag
        """
        self._children[-1].append(current)
        self._children.append([])

    def exit(self, current):
        """End of a ``with`` statement
        """
        current.add_children(self._children.pop())

    def __lshift__(self, current):
        """Add a tag to the last tag pushed by a ``with`` statement

        In:
          - ``current`` -- tag to add

        Return:
          - ``self``, the renderer
        """
        self._children[-1].append(current)

        return self

    def fromfile(self, source, tags_factory=Tag, fragment=False, no_leading_text=False, encoding='utf-8', **kw):
        """Parse a XML file

        In:
          - ``source`` -- can be a filename or a file object
          - ``fragment`` -- if ``True``, can parse a XML fragment i.e a XML without
            a unique root
          - ``no_leading_text`` -- if ``fragment`` is ``True``, ``no_leading_text``
            is ``False`` and the XML to parsed begins by a text, this text is keeped
          - ``kw`` -- keywords parameters are passed to the XML parser

        Return:
          - the root element of the parsed XML, if ``fragment`` is ``False``
          - a list of XML elements, if ``fragment`` is ``True``
        """
        if isinstance(source, (str, type(u''))):
            if source.startswith(('http://', 'https://', 'ftp://')):
                source = urlopen(source)
            else:
                source = fileopen(source, encoding=encoding)

        # Create a dedicated parser with the ``kw`` parameter
        parser = self._parser.__class__(encoding=encoding, **kw)
        # This parser will generate nodes of type ``Tag``
        parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=tags_factory))

        if not fragment:
            # Parse a tree (only one root)
            # ----------------------------

            root = etree.parse(source, parser).getroot()
            source.close()

            # Attach the renderer to the root
            root._renderer = self
            return root

        # Parse a fragment (multiple roots)
        # ---------------------------------

        # Create a dummy root
        xml = BufferIO(b'<html><body>%s</body></html>' % source.read())
        source.close()

        root = etree.parse(xml, parser).getroot()[0]
        for e in root:
            if isinstance(e, tags_factory):
                # Attach the renderer to each roots
                e._renderer = self

        # Return the children of the dummy root
        return ((root.text.encode(encoding),) if root.text and not no_leading_text else ()) + tuple(root[:])

    def fromstring(self, text, tags_factory=Tag, fragment=False, no_leading_text=False, **kw):
        """Parse a XML string

        In:
          - ``text`` -- can be a ``str`` or ``unicode`` string
          - ``fragment`` -- if ``True``, can parse a XML fragment i.e a XML without
            a unique root
          - ``no_leading_text`` -- if ``fragment`` is ``True``, ``no_leading_text``
            is ``False`` and the XML to parsed begins by a text, this text is keeped
          - ``kw`` -- keywords parameters are passed to the XML parser

        Return:
          - the root element of the parsed XML, if ``fragment`` is ``False``
          - a list of XML elements, if ``fragment`` is ``True``
        """
        if isinstance(text, type(u'')):
            text = text.encode(kw.setdefault('encoding', 'utf-8'))

        return self.fromfile(BufferIO(text), tags_factory, fragment, no_leading_text, **kw)

    @staticmethod
    def start_rendering(*args, **kw):
        pass

    @staticmethod
    def end_rendering(rendering, *args, **kw):
        return rendering

# ---------------------------------------------------------------------------


class Renderer(XmlRenderer):
    """The XML Renderer

    This renderer generate any tags you give

    .. code-block:: pycon

       >>> xml = xml.Renderer()
       >>> xml.foo(xml.bar).tostring()
       '<foo><bar/></foo>'
    """

    def __getattr__(self, name):
        """Any attribute access becomes a tag generation

        In:
          - ``name`` -- name of the tag to generate

        Return:
          - the generated tag
        """
        return self.makeelement(name)

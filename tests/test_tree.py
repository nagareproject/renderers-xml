# --
# Copyright (c) 2008-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.renderers import xml


def test_flatten():
    def g(n):
        for i in range(n):
            yield i

    assert list(xml.flatten([], None)) == []
    assert list(xml.flatten([42], None)) == [42]
    assert list(xml.flatten([42, 'hello', 'world', 10.0], None)) == [42, 'hello', 'world', 10.0]
    assert list(xml.flatten([42, [], (), g(0), 10.0], None)) == [42, 10.0]
    assert list(xml.flatten([42, [1, 2], (3, 4), g(3), 10.0], None)) == [42, 1, 2, 3, 4, 0, 1, 2, 10.0]
    assert list(xml.flatten([42, [1, (3, g(3), 4), 2], 10.0], None)) == [42, 1, 3, 0, 1, 2, 4, 2, 10.0]


def test_root1():
    x = xml.Renderer()

    foo = x.foo
    assert foo.root is foo

    bar = x.bar
    foo = x.foo(bar)
    assert foo.root is foo
    assert bar.root is foo


def test_root2():
    """One element"""
    x = xml.Renderer()
    x << x.node()

    assert not isinstance(x.root, list)


def test_root3():
    """Two elements"""
    x = xml.Renderer()
    x << x.node()
    x << x.node()

    assert isinstance(x.root, list)


def test_renderer():
    x = xml.Renderer()

    foo = x.foo
    assert hasattr(foo, '_renderer')
    assert foo.renderer is x

    bar = x.bar
    foo = x.foo(bar)
    assert hasattr(foo, '_renderer')
    assert hasattr(bar, '_renderer')
    assert foo.renderer is x
    assert bar.renderer is x

    del bar
    assert hasattr(foo, '_renderer')
    assert not hasattr(foo[0], '_renderer')
    assert foo.renderer is x
    assert foo[0].renderer is x


def test_append_text1():
    """Append text to an empty node"""
    x = xml.Renderer()

    node = x.node('test')
    assert node.text == 'test'
    assert node.tostring() == b'<node>test</node>'


def test_append_text2():
    """Append text to node with text child"""
    x = xml.Renderer()

    node = x.node('test1')
    node('test2')
    assert node.text == 'test1test2'
    assert node.tostring() == b'<node>test1test2</node>'


def test_append_text3():
    """Append text to node with node child"""
    x = xml.Renderer()

    node = x.node(x.child())
    node('test')
    assert node.getchildren()[0].tail == 'test'
    assert node.tostring() == b'<node><child/>test</node>'


def test_append4():
    """Append text to node with text & node children"""
    x = xml.Renderer()

    node = x.node(['test1', x.child()])
    node('test2')
    assert node.text == 'test1'
    assert node.getchildren()[0].tail == 'test2'
    assert node.tostring() == b'<node>test1<child/>test2</node>'


def test_add_children():
    x = xml.Renderer()

    foo = x.foo
    foo.add_children([])
    assert foo.tostring() == b'<foo/>'

    foo = x.foo
    foo.add_children(['hello', 'world'])
    assert foo.tostring() == b'<foo>helloworld</foo>'

    foo = x.foo
    foo.add_children(['hello', x.bar, 'world'])
    assert foo.tostring() == b'<foo>hello<bar/>world</foo>'

    class C(object):
        def __str__(self):
            return '[C]'

    foo = x.foo
    foo.add_children(['hello', 42, 10.0, None, C(), 2**40 - 1, u'world'])
    assert foo.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    foo = x.foo
    foo.add_children([42, [1, 2], (3, 4), 10.0])
    assert foo.tostring() == b'<foo>42123410.0</foo>'

    foo = x.foo
    foo.add_children([], {'a': 'hello'})
    assert foo.tostring() == b'<foo a="hello"/>'

    foo = x.foo
    foo.add_children([], {'a_': 'hello'})
    assert foo.tostring() == b'<foo a_="hello"/>'

    foo = x.foo
    foo.add_children([], {'a': 42})
    assert foo.tostring() == b'<foo a="42"/>'

    foo = x.foo
    foo.add_children([], {'a': 10.0})
    assert foo.tostring() == b'<foo a="10.0"/>'

    foo = x.foo
    foo.add_children([], {'a': None})
    assert foo.tostring() == b'<foo a="None"/>'

    foo = x.foo
    foo.add_children([], {'a': C()})
    assert foo.tostring() == b'<foo a="[C]"/>'

    foo = x.foo
    foo.add_children([], {'a': 2**40 - 1})
    assert foo.tostring() == b'<foo a="1099511627775"/>'

    foo = x.foo
    foo.add_children([{'a': 'hello'}])
    assert foo.tostring() == b'<foo a="hello"/>'

    foo = x.foo
    foo.add_children([{'a': 42}])
    assert foo.tostring() == b'<foo a="42"/>'

    foo = x.foo
    foo.add_children([{'a': 10.0}])
    assert foo.tostring() == b'<foo a="10.0"/>'

    foo = x.foo
    foo.add_children([{'a': None}])
    assert foo.tostring() == b'<foo a="None"/>'

    foo = x.foo
    foo.add_children([{'a': C()}])
    assert foo.tostring() == b'<foo a="[C]"/>'

    foo = x.foo
    foo.add_children([{'a': 2**40 - 1}])
    assert foo.tostring() == b'<foo a="1099511627775"/>'


def test_call():
    x = xml.Renderer()

    foo = x.foo
    assert foo.tostring() == b'<foo/>'

    foo = x.foo()
    assert foo.tostring() == b'<foo/>'

    foo = x.foo('hello', 'world')
    assert foo.tostring() == b'<foo>helloworld</foo>'

    foo = x.foo('hello', x.bar, 'world')
    assert foo.tostring() == b'<foo>hello<bar/>world</foo>'

    class C(object):
        def __str__(self):
            return '[C]'

    foo = x.foo('hello', 42, 10.0, None, C(), 2**40 - 1, u'world')
    assert foo.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    foo = x.foo(['hello', 42, 10.0, None, C(), 2**40 - 1, u'world'])
    assert foo.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    foo = x.foo(('hello', 42, 10.0, None, C(), 2**40 - 1, u'world'))
    assert foo.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    def g(n):
        for i in range(n):
            yield i

    foo = x.foo([42, [1, 2], (3, 'hello'), g(3), x.bar, 10.0])
    assert foo.tostring() == b'<foo>42123hello012<bar/>10.0</foo>'

    foo = x.foo([42, [1, (3, g(3), 'hello'), x.bar], 10.0])
    assert foo.tostring() == b'<foo>4213012hello<bar/>10.0</foo>'

    foo = x.foo({'a': 'hello'})
    assert foo.tostring() == b'<foo a="hello"/>'

    foo = x.foo({'a_': 'hello'})
    assert foo.tostring() == b'<foo a_="hello"/>'

    foo = x.foo(a='hello')
    assert foo.tostring() == b'<foo a="hello"/>'

    foo = x.foo(a_='hello')
    assert foo.tostring() == b'<foo a="hello"/>'

    foo = x.foo
    foo.add_children([], {'a': 42})
    assert foo.tostring() == b'<foo a="42"/>'

    foo = x.foo(a=10.0)
    assert foo.tostring() == b'<foo a="10.0"/>'

    foo = x.foo(a=None)
    assert foo.tostring() == b'<foo a="None"/>'

    foo = x.foo(a=C())
    assert foo.tostring() == b'<foo a="[C]"/>'

    foo = x.foo(a=2**40 - 1)
    assert foo.tostring() == b'<foo a="1099511627775"/>'

    tree = x.foo('hello', x.bar(a=10), 'world', {'b': 42}, x.bar('bar'))
    assert tree.tostring() == b'<foo b="42">hello<bar a="10"/>world<bar>bar</bar></foo>'


def test_with():
    x = xml.Renderer()
    with x.foo:
        pass
    assert x.root.tostring() == b'<foo/>'

    x = xml.Renderer()
    with x.foo():
        pass
    assert x.root.tostring() == b'<foo/>'

    x = xml.Renderer()
    with x.foo:
        x << 'hello'
        x << 'world'
    assert x.root.tostring() == b'<foo>helloworld</foo>'

    x = xml.Renderer()
    with x.foo:
        x << 'hello' << 'world'
    assert x.root.tostring() == b'<foo>helloworld</foo>'

    x = xml.Renderer()
    with x.foo:
        x << 'hello'
        x << x.bar
        x << 'world'
    assert x.root.tostring() == b'<foo>hello<bar/>world</foo>'

    class C(object):
        def __str__(self):
            return '[C]'

    x = xml.Renderer()
    with x.foo:
        x << 'hello' << 42 << 10.0
        x << None
        x << C()
        x << 2**40 - 1 << u'world'
    assert x.root.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    x = xml.Renderer()
    with x.foo:
        x << ['hello', 42, 10.0, None, C(), 2**40 - 1, u'world']
    assert x.root.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    x = xml.Renderer()
    with x.foo:
        x << ('hello', 42, 10.0, None, C(), 2**40 - 1, u'world')
    assert x.root.tostring() == b'<foo>hello4210.0[C]1099511627775world</foo>'

    def g(n):
        for i in range(n):
            yield i

    x = xml.Renderer()
    with x.foo:
        x << [42, [1, 2], (3, 'hello'), g(3), x.bar, 10.0]
    assert x.root.tostring() == b'<foo>42123hello012<bar/>10.0</foo>'

    x = xml.Renderer()
    with x.foo:
        x << [42, [1, (3, g(3), 'hello'), x.bar], 10.0]
    assert x.root.tostring() == b'<foo>4213012hello<bar/>10.0</foo>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': 'hello'}
    assert x.root.tostring() == b'<foo a="hello"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a_': 'hello'}
    assert x.root.tostring() == b'<foo a_="hello"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': 42}
    assert x.root.tostring() == b'<foo a="42"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': 10.0}
    assert x.root.tostring() == b'<foo a="10.0"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': None}
    assert x.root.tostring() == b'<foo a="None"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': C()}
    assert x.root.tostring() == b'<foo a="[C]"/>'

    x = xml.Renderer()
    with x.foo:
        x << {'a': 2**40 - 1}
    assert x.root.tostring() == b'<foo a="1099511627775"/>'

    x = xml.Renderer()
    with x.foo('hello'):
        x << x.bar(a=10) << 'world'
        x << {'b': 42}
        with x.bar:
            x << 'bar'
    assert x.root.tostring() == b'<foo b="42">hello<bar a="10"/>world<bar>bar</bar></foo>'

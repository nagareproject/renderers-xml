# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.renderers import xml


xml_test1_in = """
    <node xmlns:meld="http://www.plope.com/software/meld3">
      <child meld:id="child"/>
    </node>
"""


def test_findmeld1():
    """One element"""
    x = xml.Renderer()
    node = x.fromstring(xml_test1_in)
    child = node.findmeld('child')
    assert child is not None


def test_findmeld2():
    """Zero element"""
    x = xml.Renderer()
    node = x.fromstring("""<node xmlns:meld="http://www.plope.com/software/meld3"></node>""")
    child = node.findmeld('child')
    assert child is None


def test_findmeld3():
    """Zero element and default argument"""
    x = xml.Renderer()
    node = x.fromstring("""<node xmlns:meld="http://www.plope.com/software/meld3"></node>""")
    child = node.findmeld('child', 'test')
    assert child == 'test'


def test_replace1():
    """Replace simple node by node"""
    x = xml.Renderer()

    child1 = x.child1()
    node = x.node(child1)
    assert node.getchildren()[0] == child1
    child2 = x.child2()
    child1.replace(child2)
    assert node.getchildren()[0] == child2
    assert node.tostring() == b'<node><child2/></node>'


def test_replace2():
    """Replace simple node with text before by node"""
    x = xml.Renderer()

    child1 = x.child1()
    node = x.node('test', child1)
    assert node.getchildren()[0] == child1
    child2 = x.child2()
    child1.replace(child2)
    assert node.getchildren()[0] == child2
    assert node.tostring() == b'<node>test<child2/></node>'


def test_replace3():
    """Replace simple node with text after by node"""
    x = xml.Renderer()

    child1 = x.child1()
    node = x.node(child1, 'test')
    assert node.getchildren()[0] == child1
    child2 = x.child2()
    child1.replace(child2)
    assert node.getchildren()[0] == child2
    assert node.tostring() == b'<node><child2/>test</node>'


def test_replace4():
    """Replace simple node by text"""
    x = xml.Renderer()

    child1 = x.child1()
    node = x.node(child1)
    assert node.getchildren()[0] == child1
    child1.replace('test')
    assert node.text == 'test'
    assert node.tostring() == b'<node>test</node>'


def test_replace5():
    """Replace simple node by node + text"""
    x = xml.Renderer()

    child1 = x.child1()
    node = x.node(child1)
    assert node.getchildren()[0] == child1
    child2 = x.child2()
    child1.replace('test', child2)
    assert node.text == 'test'
    assert node.tostring() == b'<node>test<child2/></node>'


def test_replace6():
    """Replace root node"""
    x = xml.Renderer()

    node = x.node()
    node.replace('test')
    assert node.tostring() == b'<node/>'


def test_replace7():
    x = xml.Renderer()

    t1 = x.fromstring('<a>before<x>kjkjkl</x>#<b b="b">hello</b>after</a>')
    t2 = x.fromstring('<toto>xxx<titi a="a">world</titi>yyy</toto>')

    t1[1].replace(t2[0])
    # t1[1].replace('new')
    # t1[1].replace()

    assert t1.tostring() == b'<a>before<x>kjkjkl</x>#<titi a="a">world</titi>after</a>'


def test_repeat1():
    """Repeat with 2 simple text, use childname argument"""
    x = xml.Renderer()

    node = x.fromstring(xml_test1_in)
    iterator = node.repeat(['test1', 'test2'], childname='child')

    for child, value in iterator:
        child(value)
    assert [child.text for child in node.getchildren()] == ['test1', 'test2']


def test_repeat2():
    """Repeat with 2 simple text, don't use childname argument"""
    x = xml.Renderer()

    node = x.fromstring(xml_test1_in)
    child = node.findmeld('child')
    iterator = child.repeat(['test1', 'test2'])

    for child, value in iterator:
        child(value)
    assert [child.text for child in node.getchildren()] == ['test1', 'test2']


def test_repeat3():
    """Findmeld in repeat loop"""
    h = xml.Renderer()

    xhtml_tree_2 = '<div xmlns:meld="http://www.plope.com/software/meld3"><ul><li meld:id="entry"><span meld:id="count">count</span></li></ul></div>'

    root = h.fromstring(xhtml_tree_2, fragment=True)[0]

    for elem, count in root.repeat(range(2), 'entry'):
        elem.findmeld('count').fill(count)

    h << root

    assert h.root.tostring() == b'<div xmlns:meld="http://www.plope.com/software/meld3"><ul><li meld:id="entry"><span meld:id="count">0</span></li><li meld:id="entry"><span meld:id="count">1</span></li></ul></div>'
    assert h.root.tostring(pipeline=False) == b'<div xmlns:meld="http://www.plope.com/software/meld3"><ul><li><span>0</span></li><li><span>1</span></li></ul></div>'


def test_namespaces():
    x = xml.Renderer()
    x.namespaces = {'meld': xml.MELD_NS}

    with x.contacts:
        with x.contact.meld_id('contact'):
            x << x.name.meld_id('name')
            with x.address.meld_id('addr'):
                x << 'ici, rennes'

    result = b'''
    <contacts xmlns:meld="http://www.plope.com/software/meld3">
      <contact meld:id="contact">
        <name meld:id="name"/>
        <address meld:id="addr">ici, rennes</address>
      </contact>
    </contacts>
    '''

    result = b''.join(line.lstrip() for line in result.splitlines())
    assert x.root.tostring(xml_declaration=False) == result
    assert x.root.tostring(xml_declaration=True) == b"<?xml version='1.0' encoding='utf-8'?>\n" + result


def test_repeat4():
    x = xml.Renderer()

    with x.contacts:
        with x.contact.meld_id('contact'):
            x << x.name.meld_id('name')
            with x.address.meld_id('addr'):
                x << 'ici, rennes'

    for e, (name, addr) in x.root.repeat((('bill', 'seatle'), ('steve', 'cupertino')), 'contact'):
        e.findmeld('name').text = name
        e.findmeld('addr').text = addr

    result = b'''
    <contacts>
      <contact xmlns:ns0="http://www.plope.com/software/meld3" ns0:id="contact">
        <name ns0:id="name">bill</name>
        <address ns0:id="addr">seatle</address>
      </contact>
      <contact xmlns:ns0="http://www.plope.com/software/meld3" ns0:id="contact">
        <name ns0:id="name">steve</name>
        <address ns0:id="addr">cupertino</address>
      </contact>
    </contacts>'''

    result = b''.join(line.lstrip() for line in result.splitlines())
    assert x.root.tostring() == result

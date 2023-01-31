# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os

from lxml import etree
from nagare.renderers import xml


def test_parse_xmlstring1():
    """Good encoding"""
    try:
        x = xml.Renderer()
        f = open(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml'))
        x.fromstring(f.read())
        f.close()
    except UnicodeDecodeError:
        assert False
    else:
        assert True


def test_parse_xml1():
    """Good encoding"""
    try:
        x = xml.Renderer()
        x.fromfile(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml'))
    except UnicodeDecodeError:
        assert False
    else:
        assert True


def test_parse_xmlstring2():
    """Bad encoding"""
    try:
        x = xml.Renderer()
        f = open(os.path.join(os.path.dirname(__file__), 'iso-8859.xml'))
        x.fromfile(f, encoding='utf-8')
        f.close()
    except (etree.XMLSyntaxError, UnicodeDecodeError):
        assert True
    else:
        assert False


xml_fragments_1 = 'leading_text<fragment1></fragment1>text<fragment2></fragment2>'


def test_parse_xmlstring3():
    """Parse fragment xml with fragment flag"""
    x = xml.Renderer()
    roots = x.fromstring(xml_fragments_1, fragment=True)
    assert roots[0] == b'leading_text'
    assert roots[1].tostring() == b'<fragment1/>text'
    assert roots[1].tail == 'text'
    assert roots[2].tostring() == b'<fragment2/>'


def test_parse_xmlstring4():
    """Parse xml tree with fragment flag"""
    x = xml.Renderer()
    roots = x.fromstring(xml_fragments_1, fragment=True, no_leading_text=True)
    assert roots[0].tostring() == b'<fragment1/>text'
    assert roots[0].tail == 'text'
    assert roots[1].tostring() == b'<fragment2/>'


def test_parse_xmlstring5():
    """Test parse child type"""
    x = xml.Renderer()
    root = x.fromstring('<a>text</a>')
    assert type(root) == xml.Tag

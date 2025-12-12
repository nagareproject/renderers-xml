# --
# Copyright (c) 2008-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import csv

from nagare.renderers import xml

xml_test2_in = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
          xmlns:meld="http://www.plope.com/software/meld3"
          xmlns:bar="http://foo/bar">
      <head>
        <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type" />
        <title meld:id="title">This is the title</title>
      </head>
      <body>
        <div/> <!-- empty tag -->
        <div meld:id="content_well">
          <form meld:id="form1" action="." method="POST">
          <table border="0" meld:id="table1">
            <tbody meld:id="tbody">
              <tr>
                <th>Name</th>
                <th>Description</th>
              </tr>
              <tr meld:id="tr" class="foo">
                <td meld:id="td1">Name</td>
                <td meld:id="td2">Description</td>
              </tr>
            </tbody>
          </table>
          <input type="submit" name="next" value=" Next "/>
          </form>
        </div>
      </body>
    </html>"""


def test_global1():
    """Create xml by procedural way."""
    x = xml.Renderer()

    file_path = os.path.join(os.path.dirname(__file__), 'helloworld.csv')

    reader = csv.reader(open(file_path, 'r'))

    with x.hello:
        for row in reader:
            with x.world(language=row[0]):
                x << row[1]

    xml_to_test = x.root.tostring(xml_declaration=True, pretty_print=True)

    with open(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml'), 'rb') as f:
        xml_to_compare = f.read()
    assert xml_to_test == xml_to_compare


def test_global2():
    """Create xml by functionnal way."""
    x = xml.Renderer()

    file_path = os.path.join(os.path.dirname(__file__), 'helloworld.csv')

    reader = csv.reader(open(file_path))

    root = x.hello([x.world(row[1], {'language': row[0]}) for row in reader])

    xml_to_test = root.tostring(xml_declaration=True, pretty_print=True)

    with open(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml'), 'rb') as f:
        xml_to_compare = f.read()
    assert xml_to_test == xml_to_compare


def test_global3():
    """Test parse() method."""
    x = xml.Renderer()

    with open(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml')) as f:
        root = x.fromstring(f.read())

    xml_to_test = root.tostring(xml_declaration=True, pretty_print=True)

    with open(os.path.join(os.path.dirname(__file__), 'test_xmlns_1.xml'), 'rb') as f:
        xml_to_compare = f.read()
    assert xml_to_test == xml_to_compare


def test_global4():
    """Test findmeld() with children affectation."""
    x = xml.Renderer()
    root = x.fromstring(xml_test2_in)

    root.findmeld('title').text = 'My document'
    root.findmeld('form1').set('action', './handler')
    data = ({'name': 'Girls', 'description': 'Pretty'}, {'name': 'Boys', 'description': 'Ugly'})

    iterator = root.findmeld('tr').repeat(data)
    for element, item in iterator:
        td1 = element.findmeld('td1')
        td1.text = item['name']
        element.findmeld('td2').text = item['description']

    assert [elt.text for elt in root.xpath('.//x:td', namespaces={'x': 'http://www.w3.org/1999/xhtml'})] == [
        'Girls',
        'Pretty',
        'Boys',
        'Ugly',
    ]
    assert root[0][1].text == 'My document'
    assert root.xpath('.//x:form', namespaces={'x': 'http://www.w3.org/1999/xhtml'})[0].attrib['action'] == './handler'


def test_global5():
    """Test findmeld() & replace()."""
    x = xml.Renderer()
    root = x.fromstring(xml_test2_in)

    root.findmeld('title').text = 'My document'
    root.findmeld('form1').set('action', './handler')

    data = ({'name': 'Girls', 'description': 'Pretty'}, {'name': 'Boys', 'description': 'Ugly'})

    children = []
    for elt in data:
        children.append(x.tr([x.td(elt['name']), x.td(elt['description'])], {'class': 'bar'}))

    root.findmeld('tr').replace(children)

    assert root.findall('.//tr')[1].attrib['class'] == 'bar'
    assert [elt.text for elt in root.xpath('.//td')] == ['Girls', 'Pretty', 'Boys', 'Ugly']


def test_global6():
    """Test tostring() with option pipeline=False."""
    x = xml.Renderer()
    root = x.fromstring(xml_test2_in)

    root.findmeld('title').text = 'My document'
    root.findmeld('form1').set('action', './handler')

    data = ({'name': 'Girls', 'description': 'Pretty'}, {'name': 'Boys', 'description': 'Ugly'})

    children = []
    for elt in data:
        children.append(x.tr([x.td(elt['name']), x.td(elt['description'])], {'class': 'bar'}))

    root.findmeld('tr').replace(children)

    root.tostring(xml_declaration=True, pretty_print=True, pipeline=False)

    assert root.findmeld('tr') is None
    assert root.findmeld('content_well') is None


def test_global7():
    """Test tostring() with option pipeline=True."""
    x = xml.Renderer()
    root = x.fromstring(xml_test2_in)

    root.findmeld('title').text = 'My document'
    root.findmeld('form1').set('action', './handler')

    data = ({'name': 'Girls', 'description': 'Pretty'}, {'name': 'Boys', 'description': 'Ugly'})

    children = []
    for elt in data:
        children.append(x.tr([x.td(elt['name']), x.td(elt['description'])], {'class': 'bar'}))

    root.findmeld('tr').replace(children)

    root.tostring(xml_declaration=True, pretty_print=True, pipeline=True)

    assert root.findmeld('tr') is None
    assert root.findmeld('content_well') is not None


def test_global8():
    """Create xml."""
    x = xml.Renderer()
    x.namespaces = {'meld': 'http://www.plope.com/software/meld3'}
    data = ({'name': 'Girls', 'description': 'Pretty'}, {'name': 'Boys', 'description': 'Ugly'})

    with x.html:
        with x.head:
            with x.meta:
                x << {'content': 'text/html; charset=ISO-8859-1', 'http-equiv': 'content-type'}
            with x.title.meld_id('title'):
                x << 'My document'
        with x.body:
            with x.div:
                pass
            x << x.comment(' empty tag ')
            with x.div, x.form.meld_id('form1'):
                x << {'action': './handler'}
                with x.table, x.tbody:
                    with x.tr:
                        x << x.th('Name') << x.th('Description')
                    for elt in data:
                        with x.tr.meld_id('tr'):
                            x << x.td(elt['name']).meld_id('td') << x.td(elt['description']).meld_id('td')
                with x.input:
                    x << {'type': 'submit', 'name': 'next', 'value': ' Next '}

    assert [elt.text for elt in x.root.xpath('.//td')] == ['Girls', 'Pretty', 'Boys', 'Ugly']
    assert x.root[0][1].text == 'My document'
    assert x.root.xpath('.//form')[0].attrib['action'] == './handler'

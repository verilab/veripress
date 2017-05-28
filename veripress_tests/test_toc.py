import re

from veripress.model.toc import HtmlTocParser


def html_same(html1, html2):
    return re.sub('\s', '', html1) == re.sub('\s', '', html2)


html_example = """
<h6>a very small title</h6>
<h1>Title</h1>
  <h2>Title</h2>
    <h4>Another title, yes!</h4>
    <h3>中文，标题 Title&amp;</h3>
      <p>a random paragraph...<br/></p>
      &amp; &#60;
      <!-- comment -->
<h1>Another-h1-1</h1>
  <h5>a very small title</h5>
"""


def test_toc_parser():
    parser = HtmlTocParser()
    parser.feed('')
    assert parser.toc() == []
    assert parser.toc_html() == ''

    parser = HtmlTocParser()
    parser.feed('<a href="#">no-effect</a>')
    assert html_same(parser.html, '<a href="#">no-effect</a>')

    parser.feed('<h1>Title</h1>')
    assert html_same(parser.html,
                     '<a href="#">no-effect</a><h1><a id="Title" href="#Title" class="anchor"></a>Title</h1>')

    parser = HtmlTocParser()
    parser.feed(html_example)
    expected_toc = [{'level': 6, 'id': 'a-very-small-title', 'data': 'a very small title', 'children': []},
                    {'level': 1, 'id': 'Title', 'data': 'Title', 'children': [
                        {'level': 2, 'id': 'Title_1', 'data': 'Title', 'children': [
                            {'level': 4, 'id': 'Another-title-yes', 'data': 'Another title, yes!', 'children': []},
                            {'level': 3, 'id': '中文-标题-Title-amp', 'data': '中文，标题 Title&amp;', 'children': []}
                        ]}
                    ]},
                    {'level': 1, 'id': 'Another-h1-1', 'data': 'Another-h1-1', 'children': [
                        {'level': 5, 'id': 'a-very-small-title_1', 'data': 'a very small title', 'children': []}
                    ]}]
    assert parser.toc() == expected_toc

    expected_toc_html = """
    <ul>
      <li><a href="#Title">Title</a>
        <ul>
          <li><a href="#Title_1">Title</a></li>
        </ul>
      </li>
      <li><a href="#Another-h1-1">Another-h1-1</a>
        <ul>
          <li><a href="#a-very-small-title_1">a very small title</a></li>
        </ul>
      </li>
    </ul>
    """
    assert html_same(parser.toc_html(depth=2, lowest_level=5), expected_toc_html)

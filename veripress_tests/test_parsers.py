import re

import mistune
from pytest import raises

from veripress.model.parsers import get_standard_format_name, get_parser, Parser, TxtParser, MarkdownParser, parser


def test_parser_decorator():
    class FakeParser:
        pass

    parser('FoRMat1')(FakeParser)
    assert get_standard_format_name('formAT1') == 'format1'
    parser('format2', ext_names='fmt2')(FakeParser)
    assert get_standard_format_name('fmt2') == 'format2'
    parser('format3', ext_names=['fmt3', 'f3'])(FakeParser)
    assert get_standard_format_name('fmt3') == 'format3'
    assert get_standard_format_name('f3') == 'format3'


def test_base_parser():
    p = Parser()
    with raises(NotImplementedError):
        assert p.parse_preview('abc')
    with raises(NotImplementedError):
        assert p.parse_whole('abc')

    assert p.remove_read_more_sep('abc') == 'abc'


def test_get_standard_format_name():
    assert get_standard_format_name('txt') == 'txt'
    assert get_standard_format_name('TxT') == 'txt'
    assert get_standard_format_name('md') == 'markdown'
    assert get_standard_format_name('MDown') == 'markdown'
    assert get_standard_format_name('Markdown') == 'markdown'


def test_get_parser():
    assert isinstance(get_parser('txt'), TxtParser)
    assert isinstance(get_parser('markdown'), MarkdownParser)
    assert get_parser('non-exists') is None


def test_txt_parser():
    p = TxtParser()
    raw_content = 'abc'
    preview, has_more_content = p.parse_preview(raw_content)
    assert preview == p.parse_whole(raw_content) == '<pre>abc</pre>'
    assert has_more_content is False
    raw_content = 'abc\n---more---\n\ndef'
    assert p.parse_preview(raw_content) == ('<pre>abc</pre>', True)
    assert p.parse_whole(raw_content) == '<pre>abc\n\ndef</pre>'
    raw_content = 'abc\n------ MoRe     ---  \n\ndef---more ---'
    assert p.parse_whole(raw_content) == '<pre>abc\n\ndef---more ---</pre>'


def test_md_parser():
    renderer = MarkdownParser.HighlightRenderer()
    md = mistune.Markdown(renderer=renderer)
    assert md('```\nabc\n```').strip() == '<pre><code>abc</code></pre>'
    assert re.sub('\s*', '', md('```python\nprint()\n```')) \
           == re.sub('\s*', '', '<div class="highlight"><pre>'
                                '<span></span><span class="k">print</span><span class="p">()</span>'
                                '</pre></div>')

    p = MarkdownParser()
    assert p.parse_whole('## hello\n\n[link](https://google.com)').strip() \
           == '<h2>hello</h2>\n<p><a href="https://google.com">link</a></p>'

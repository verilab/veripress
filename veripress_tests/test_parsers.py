from veripress.model.parsers import get_standard_format_name, get_parser, Parser, TxtParser, MarkdownParser


def test_base_parser():
    p = Parser()
    assert p.parse_preview('abc') == p.parse_whole('abc') == 'abc'


def test_get_standard_format_name():
    assert get_standard_format_name('txt') == 'txt'
    assert get_standard_format_name('TxT') == 'txt'
    assert get_standard_format_name('md') == 'markdown'
    assert get_standard_format_name('MDown') == 'markdown'
    assert get_standard_format_name('Markdown') == 'markdown'

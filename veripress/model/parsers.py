import re

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

from veripress.helpers import to_list


class Parser(object):
    """Base parser class."""

    # this should be overridden in subclasses, and should be a compiled regular expression
    _read_more_exp = None

    def parse_preview(self, raw_content):
        """Simply returns the raw preview part of the content."""
        if self._read_more_exp is None:
            return self.parse_whole(raw_content)

        sp = self._read_more_exp.split(raw_content, maxsplit=1)
        if len(sp) == 2 and sp[0]:
            result = sp[0].rstrip()
        else:
            result = raw_content
        # since the preview part contains no read_more_sep, we can safely use the parse_whole method
        return self.parse_whole(result)

    def parse_whole(self, raw_content):
        """Parse the whole part of the content. Should be overridden in subclasses."""
        raise NotImplementedError

    def preprocess_whole_content(self, raw_content):
        """
        Removes the first read_more_sep that occurs in raw_content.
        Subclasses should call this method to preprocess raw_content.
        """
        if self._read_more_exp is None:
            return raw_content

        sp = self._read_more_exp.split(raw_content, maxsplit=1)
        if len(sp) == 2 and sp[0]:
            result = '\n\n'.join((sp[0].rstrip(), sp[1].lstrip()))
        else:
            result = raw_content
        return result


_ext_format_mapping = {}  # key: extension name, value: standard format name
_format_parser_mapping = {}  # key: standard format name, value: parser instance


def get_standard_format_name(ext_name):
    """
    Get the standard format name of the given extension.

    :param ext_name: extension name
    :return: standard format name
    """
    return _ext_format_mapping.get(ext_name.lower())


def get_parser(format_name):
    """
    Get parser of the given format.

    :param format_name: standard format name
    :return: the parser instance
    """
    return _format_parser_mapping.get(format_name.lower())


def parser(format_name, ext_names=None):
    """
    Decorate a parser class to register it.

    :param format_name: standard format name
    :param ext_names: supported extension name
    """

    def decorator(cls):
        format_name_lower = format_name.lower()
        if ext_names is None:
            _ext_format_mapping[format_name_lower] = format_name_lower
        else:
            for ext in to_list(ext_names):
                _ext_format_mapping[ext.lower()] = format_name_lower
        _format_parser_mapping[format_name_lower] = cls()
        return cls

    return decorator


@parser('txt', ext_names=['txt'])
class TxtParser(Parser):
    """Txt content parser."""

    _read_more_exp = re.compile('-{3,}[ \t]*more[ \t]*-{3,}', re.IGNORECASE)

    def parse_whole(self, raw_content):
        raw_content = self.preprocess_whole_content(raw_content)
        return '<pre>{}</pre>'.format(raw_content)


@parser('markdown', ext_names=['md', 'mdown', 'markdown'])
class MarkdownParser(Parser):
    """Markdown content parser."""

    _read_more_exp = re.compile('<!--\s*more\s*-->', re.IGNORECASE)

    class HighlightRenderer(mistune.Renderer):
        """Custom mistune render to parse block code."""

        def block_code(self, code, lang=None):
            if not lang:
                return '\n<pre><code>{}</code></pre>\n'.format(mistune.escape(code))
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = html.HtmlFormatter()
            return highlight(code, lexer, formatter)

    _renderer = HighlightRenderer()
    _markdown = mistune.Markdown(renderer=_renderer)

    def parse_whole(self, raw_content):
        raw_content = self.preprocess_whole_content(raw_content)
        return self._markdown(raw_content)

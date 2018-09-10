import re
from functools import partial

import markdown

from veripress.helpers import to_list


class Parser(object):
    """Base parser class."""

    # this should be overridden in subclasses,
    # and should be a compiled regular expression
    _read_more_exp = None

    def __init__(self):
        if self._read_more_exp is not None and \
                isinstance(self._read_more_exp, str):
            # compile the regular expression
            # make the regex require new lines above and below the sep flag
            self._read_more_exp = re.compile(
                r'\r?\n\s*?' + self._read_more_exp + r'\s*?\r?\n',
                re.IGNORECASE
            )

    def parse_preview(self, raw_content):
        """
        Parse the preview part of the content,
        and return the parsed string and whether there is more content or not.

        If the preview part is equal to the whole part,
        the second element of the returned tuple will be False, else True.

        :param raw_content: raw content
        :return: tuple(parsed string, whether there is more content or not)
        """
        if self._read_more_exp is None:
            return self.parse_whole(raw_content), False

        sp = self._read_more_exp.split(raw_content, maxsplit=1)
        if len(sp) == 2 and sp[0]:
            has_more_content = True
            result = sp[0].rstrip()
        else:
            has_more_content = False
            result = raw_content
        # since the preview part contains no read_more_sep,
        # we can safely use the parse_whole method
        return self.parse_whole(result), has_more_content

    def parse_whole(self, raw_content):
        """
        Parse the whole part of the content.
        Should be overridden in subclasses.
        """
        raise NotImplementedError

    def remove_read_more_sep(self, raw_content):
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


# key: extension name, value: standard format name
_ext_format_mapping = {}
# key: standard format name, value: parser instance
_format_parser_mapping = {}


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

    _read_more_exp = r'-{3,}[ \t]*more[ \t]*-{3,}'

    def parse_whole(self, raw_content):
        raw_content = self.remove_read_more_sep(raw_content)
        return '<pre class="txt">{}</pre>'.format(raw_content)


@parser('markdown', ext_names=['md', 'mdown', 'markdown'])
class MarkdownParser(Parser):
    """Markdown content parser."""

    _read_more_exp = r'<!--\s*more\s*-->'

    _markdown = partial(
        markdown.markdown,
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite'
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'guess_lang': False,
                'css_class': 'highlight',
                'use_pygments': True
            }
        },
    )

    def parse_whole(self, raw_content):
        raw_content = self.remove_read_more_sep(raw_content)
        return self._markdown(raw_content).strip()

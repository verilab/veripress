import re


class Parser(object):
    """
    Base parser class. Things should be overridden in subclasses.
    """

    @classmethod
    def parse_preview(cls, raw_content):
        return cls.parse_whole(raw_content)

    @classmethod
    def parse_whole(cls, raw_content):
        return raw_content


_ext_format_mapping = {}
_format_parser_mapping = {}


def get_standard_format_name(ext_name):
    """
    Get the standard format name of the given extension.

    :param ext_name: extension name
    :return: standard format name
    """
    return _ext_format_mapping.get(ext_name.lower())


def get_parser(format_name):
    return _format_parser_mapping.get(format_name.lower())


def parser(format_name, ext_names=None):
    def decorator(cls):
        format_name_lower = format_name.lower()
        if ext_names is None:
            _ext_format_mapping[format_name_lower] = format_name_lower
        elif isinstance(ext_names, str):
            _ext_format_mapping[ext_names.lower()] = format_name_lower
        else:
            for ext in ext_names:
                _ext_format_mapping[ext.lower()] = format_name_lower
        _format_parser_mapping[format_name_lower] = cls
        return cls

    return decorator


@parser('txt', ext_names=['txt'])
class TxtParser(Parser):
    _read_more_exp = re.compile('-{3,}\s*more\s*-{3,}', re.IGNORECASE | re.MULTILINE)

    @classmethod
    def parse_preview(cls, raw_content):
        sp = cls._read_more_exp.split(raw_content, maxsplit=1)
        if len(sp) == 2 and sp[0]:
            result = sp[0].rstrip()
        else:
            result = raw_content
        return '<pre>{}</pre>'.format(result)

    @classmethod
    def parse_whole(cls, raw_content: str):
        sp = cls._read_more_exp.split(raw_content, maxsplit=1)
        if len(sp) == 2 and sp[0]:
            result = '\n\n'.join((sp[0].rstrip(), sp[1].lstrip()))
        else:
            result = raw_content
        return '<pre>{}</pre>'.format(result)


@parser('markdown', ext_names=['md', 'mdown', 'markdown'])
class MarkdownParser(Parser):
    pass

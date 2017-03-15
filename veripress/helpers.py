import os
import re
from collections import Iterable
from datetime import date, datetime, timedelta, timezone


def url_rule(blueprint_or_app, rules, endpoint=None, view_func=None, **options):
    """
    Add one or more url rules to the given Flask blueprint or app.

    :param blueprint_or_app: Flask blueprint or app
    :param rules: a single rule string or a list of rules
    :param endpoint: endpoint
    :param view_func: view function
    :param options: other options
    """
    for rule in to_list(rules):
        blueprint_or_app.add_url_rule(rule, endpoint=endpoint, view_func=view_func, **options)


def to_list(item_or_list):
    """
    Convert a single item, a tuple, a generator or anything else to a list.

    :param item_or_list: single item or iterable to convert
    :return: a list
    """
    if isinstance(item_or_list, list):
        return item_or_list
    elif isinstance(item_or_list, (str, bytes)):
        return [item_or_list]
    elif isinstance(item_or_list, Iterable):
        return list(item_or_list)
    else:
        return [item_or_list]


def to_datetime(date_or_datetime):
    """
    Convert a date object to a datetime object, or return as it is if it's not a date object.

    :param date_or_datetime: date or datetime object
    :return: a datetime object
    """
    if isinstance(date_or_datetime, date) and not isinstance(date_or_datetime, datetime):
        d = date_or_datetime
        return datetime.strptime('%04d-%02d-%02d' % (d.year, d.month, d.day), '%Y-%m-%d')
    return date_or_datetime


def timezone_from_str(tz_str):
    """
    Convert a timezone string to a timezone object.

    :param tz_str: string with format 'UTC±[hh]:[mm]'
    :return: a timezone object
    """
    m = re.match('UTC([+|-]\d{1,2}):(\d{2})', tz_str)
    delta_h = int(m.group(1))
    delta_m = int(m.group(2)) if delta_h >= 0 else -int(m.group(2))
    return timezone(timedelta(hours=delta_h, minutes=delta_m))


class ConfigurationError(Exception):
    """Raise this when there's something wrong with the configuration."""
    pass


class Pair(object):
    """A class that just represent two value."""

    __dict__ = ['first', 'second']

    def __init__(self, first=None, second=None):
        self.first = first
        self.second = second

    def __repr__(self):
        return '<{} ({}, {})>'.format(Pair.__name__, repr(self.first), repr(self.second))

    def __eq__(self, other):
        if isinstance(other, Pair):
            return self.first == other.first and self.second == other.second
        return super(Pair, self).__eq__(other)

    def __iter__(self):
        return (self.first if i == 0 else self.second for i in range(2))

    def __bool__(self):
        return bool(self.first) or bool(self.second)

    def __contains__(self, item):
        return self.first == item or self.second == item

    def __add__(self, other):
        a, b = other
        return Pair(self.first + a, self.second + b)

    def __sub__(self, other):
        a, b = other
        return Pair(self.first - a, self.second - b)

    def __getitem__(self, item):
        if isinstance(item, int):
            if item == 0:
                return self.first
            elif item == 1:
                return self.second
        raise IndexError


def validate_custom_page_path(path):
    """
    Check if a custom page path is valid or not, to prevent malicious requests.

    :param path: custom page path (url path)
    :return: valid or not
    """
    sp = path.split('/')
    if '.' in sp or '..' in sp:
        return False
    return True


def traverse_directory(dir_path, yield_dir=False):
    """
    Traverse through a directory recursively.

    :param dir_path: directory path
    :param yield_dir: yield subdirectory or not
    :return: a generator
    """
    if not os.path.isdir(dir_path):
        return

    for item in os.listdir(dir_path):
        new_path = os.path.join(dir_path, item)
        if os.path.isdir(new_path):
            if yield_dir:
                yield new_path + os.path.sep
            yield from traverse_directory(new_path, yield_dir)
        else:
            yield new_path

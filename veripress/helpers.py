import os
import functools
from collections import Iterable
from datetime import date, datetime

from flask import render_template, request


def view(template=None):
    """
    Decorate a view function with a default template name.
    This will try template in the custom folder first, the theme's original ones second.

    :param template: template name
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'
            context = func(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context
            return render_template([os.path.join('custom', template_name), template_name], **context)

        return wrapper

    return decorator


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
        return datetime.strptime('-'.join([str(d.year), str(d.month), str(d.day)]), '%Y-%m-%d')
    return date_or_datetime


class ConfigurationError(Exception):
    """Raise this when there's something wrong with the configuration."""
    pass

import functools

from flask import jsonify, url_for, current_app, request

from veripress import site
from veripress.api import ApiException, json_api
from veripress.model import storage
from veripress.model.parsers import get_parser


@json_api
def site_info():
    return site


@json_api
def posts(year: int = None, month: int = None, day: int = None, post_name: str = None):
    result = storage.get_posts()

    rel_url_prefix = ''
    if year is not None:
        rel_url_prefix += '%04d/' % year
    if month is not None:
        rel_url_prefix += '%02d/' % month
    if day is not None:
        rel_url_prefix += '%02d/' % day
    if post_name is not None:
        rel_url_prefix += '%s/' % post_name
    result = filter(lambda p: p.rel_url.startswith(rel_url_prefix), result) if rel_url_prefix else result

    # TODO

    return result


def tags():
    pass


def categories():
    pass


def custom_pages(page_path):
    pass


def search():
    pass


def webhook():
    pass

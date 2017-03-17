import re
import os
from itertools import islice
from datetime import date

from flask import current_app, request, send_file

from veripress import site
from veripress.api import ApiException, Error
from veripress.model import storage
from veripress.model.models import Base
from veripress.model.parsers import get_parser
from veripress.helpers import validate_custom_page_path


def site_info():
    return site


def posts(year: int = None, month: int = None, day: int = None, post_name: str = None):
    args = {k: [x.strip() for x in v.split(',')] for k, v in request.args.items()}

    for key in ('include_draft', 'start', 'count'):
        # pop out items that should not be passed into the 'get_posts' method as 'limits'
        args.pop(key, None)
    fields = args.pop('fields', None)  # fields that the API user needs, a list or None

    for key in ('created', 'updated'):
        if key in args:
            try:
                interval = args[key]
                # should be ['2017-02-13', '2017-03-13'] if it's valid
                for i in range(2):
                    y, m, d = re.match('(\d{4})-(\d{1,2})-(\d{1,2})', interval[i]).groups()
                    interval[i] = date(year=int(y), month=int(m), day=int(d))
            except (IndexError, AttributeError, ValueError):
                raise ApiException(message='The "{}" argument is invalid, '
                                           'and it should be like "2017-02-13,2017-03-13".'.format(key),
                                   error=Error.INVALID_ARGUMENTS)

    result_posts = storage.get_posts_with_limits(include_draft=False, **args)  # get the post list here

    return_single_item = False
    rel_url_prefix = ''
    if year is not None:
        rel_url_prefix += '%04d/' % year
    if month is not None:
        rel_url_prefix += '%02d/' % month
    if day is not None:
        rel_url_prefix += '%02d/' % day
    if post_name is not None:
        rel_url_prefix += '%s/' % post_name
        return_single_item = True  # if a full relative url is given, we return just ONE post, instead of a list
    result_posts = filter(lambda p: p.rel_url.startswith(rel_url_prefix), result_posts)

    start = request.args.get('start', '')
    start = int(start) if start.isdigit() else 0
    count = request.args.get('count', '')
    count = int(count) if count.isdigit() else -1

    result_posts_list = []
    for post in islice(result_posts, start, start + count if count >= 0 else None):
        parser = get_parser(post.format)
        post_d = post.to_dict()
        del post_d['raw_content']
        if return_single_item:
            # if a certain ONE post is needed, we parse all content instead of preview
            post_d['content'] = parser.parse_whole(post.raw_content)
        else:
            # a list of posts is needed, we parse only previews
            post_d['preview'], post_d['has_more_content'] = parser.parse_preview(post.raw_content)
        if fields is not None:
            # select only needed fields to return
            assert isinstance(fields, list)
            full_post_d = post_d
            post_d = {}
            for key in fields:
                if key in full_post_d:
                    post_d[key] = full_post_d[key]
        result_posts_list.append(post_d)

    if result_posts_list and return_single_item:
        return result_posts_list[0]
    else:
        return result_posts_list if result_posts_list else None


def tags():
    return [{'name': item[0], 'published': item[1].second} for item in storage.get_tags()]


def categories():
    return [{'name': item[0], 'published': item[1].second} for item in storage.get_categories()]


def pages(page_path):
    if not validate_custom_page_path(page_path):
        raise ApiException(error=Error.NOT_ALLOWED, message='The visit of path "{}" is not allowed.'.format(page_path))

    rel_url, exists = storage.fix_relative_url('page', page_path)
    if exists:
        file_path = rel_url
        return send_file(file_path)
    elif rel_url is None:  # pragma: no cover, it seems impossible to make this happen, see code of 'fix_relative_url'
        raise ApiException(error=Error.BAD_PATH, message='The path "{}" cannot be recognized.'.format(page_path))
    else:
        page = storage.get_page(rel_url, include_draft=False)
        if page is None:
            raise ApiException(error=Error.RESOURCE_NOT_EXISTS)
        page_d = page.to_dict()
        del page_d['raw_content']
        page_d['content'] = get_parser(page.format).parse_whole(page.raw_content)
        return page_d


def widgets():
    result_widgets = storage.get_widgets(position=request.args.get('position'), include_draft=False)
    result = []
    for widget in result_widgets:
        widget_d = widget.to_dict()
        del widget_d['raw_content']
        widget_d['content'] = get_parser(widget.format).parse_whole(widget.raw_content)
        result.append(widget_d)
    return result if result else None


def search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        raise ApiException(error=Error.INVALID_ARGUMENTS, message='The "q" argument is missed or invalid.')

    start = request.args.get('start', '')
    start = int(start) if start.isdigit() else 0
    count = request.args.get('count', '')
    count = int(count) if count.isdigit() else -1

    def remove_raw_content_field(p):
        del p['raw_content']
        return p

    result = list(islice(map(remove_raw_content_field, map(Base.to_dict, storage.search_for(query))),
                         start, start + count if count >= 0 else None))
    return result if result else None

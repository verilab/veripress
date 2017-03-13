import re
from datetime import date

from flask import jsonify, url_for, current_app, request

from veripress import site
from veripress.api import ApiException, Error, json_api
from veripress.model import storage
from veripress.model.parsers import get_parser


@json_api
def site_info():
    return site


@json_api
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

    include_draft = request.args.get('include_draft', 'true').lower().strip()
    include_draft = False if include_draft in ('false', 'no', '0') else True
    result_posts = storage.get_posts_with_limits(include_draft=include_draft, **args)  # get the post list here

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
    for i, post in enumerate(result_posts):
        if count == 0:
            break
        if i >= start:
            parser = get_parser(post.format)
            post_d = post.to_dict()
            del post_d['raw_content']
            if return_single_item:
                # if a certain ONE post is needed, we parse all content instead of preview
                post_d['content'] = parser.parse_whole(post.raw_content)
            else:
                # a list of posts is needed, we parse only previews
                post_d['preview'] = parser.parse_preview(post.raw_content)

            if fields is not None:
                # select only needed fields to return
                assert isinstance(fields, list)
                full_post_d = post_d
                post_d = {}
                for key in fields:
                    if key in full_post_d:
                        post_d[key] = full_post_d[key]

            result_posts_list.append(post_d)
            count -= 1

    if result_posts_list and return_single_item:
        return result_posts_list[0]
    else:
        return result_posts_list if result_posts_list else None


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

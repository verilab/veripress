import os
from itertools import islice

from feedgen.feed import FeedGenerator
from flask import url_for, request, redirect, current_app, send_file, abort, make_response

from veripress import site, cache
from veripress.view import templated, custom_render_template
from veripress.model import storage
from veripress.model.models import Base
from veripress.model.parsers import get_parser
from veripress.model.toc import HtmlTocParser
from veripress.helpers import timezone_from_str

make_post_abs_url = lambda r: request.url_root + 'post/' + r  # 'r' means relative url (rel_url)


def parse_toc(html_content):
    """
    Parse TOC of HTML content if the SHOW_TOC config is true.

    :param html_content: raw HTML content
    :return: tuple(processed HTML, toc list, toc HTML unordered list)
    """
    if current_app.config['SHOW_TOC']:
        toc_parser = HtmlTocParser()
        toc_parser.feed(html_content)
        toc_html = toc_parser.toc_html(depth=current_app.config['TOC_DEPTH'],
                                       lowest_level=current_app.config['TOC_LOWEST_LEVEL'])
        toc = toc_parser.toc(depth=current_app.config['TOC_DEPTH'],
                             lowest_level=current_app.config['TOC_LOWEST_LEVEL'])
        return toc_parser.html, toc, toc_html
    else:
        return html_content, None, None


@templated('index.html')
@cache.memoize(timeout=2 * 60)
def index(page_num=1):
    if page_num <= 1 and request.path != '/':
        return redirect(url_for('.index'))  # redirect '/page/1' to '/'

    all_posts = storage.get_posts(include_draft=False)

    count = current_app.config['ENTRIES_PER_PAGE']
    start = (page_num - 1) * count

    posts = []
    for post_ in islice(all_posts, start, start + count + 1):  # slice an additional one to check if there is more
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_post_abs_url(post_.rel_url)
        posts.append(post_d)

    if start > 0:
        next_url = url_for('.index', page_num=page_num - 1)
    else:
        next_url = None
    if len(posts) > count:
        # the additional one is included
        posts = posts[:count]
        prev_url = url_for('.index', page_num=page_num + 1)
    else:
        prev_url = None

    return dict(entries=posts, next_url=next_url, prev_url=prev_url)


@templated('post.html')
@cache.memoize(timeout=2 * 60)
def post(year, month, day, post_name):
    rel_url = request.path[len('/post/'):]
    fixed_rel_url = storage.fix_post_relative_url(rel_url)
    if rel_url != fixed_rel_url:
        return redirect(make_post_abs_url(fixed_rel_url))  # it's not the correct relative url, so redirect

    post_ = storage.get_post(rel_url, include_draft=False)
    if post_ is None:
        abort(404)

    post_d = post_.to_dict()
    del post_d['raw_content']
    post_d['content'] = get_parser(post_.format).parse_whole(post_.raw_content)
    post_d['content'], toc, toc_html = parse_toc(post_d['content'])
    post_d['url'] = make_post_abs_url(rel_url)
    post_ = post_d

    if post_['layout'] != 'post':
        return custom_render_template(post_['layout'] + '.html', entry=post_)
    return dict(entry=post_, toc=toc, toc_html=toc_html)


@templated('page.html')
@cache.memoize(timeout=2 * 60)
def page(rel_url):
    fixed_rel_url, exists = storage.fix_page_relative_url(rel_url)
    if exists:
        return send_file(os.path.join(current_app.instance_path, 'pages', fixed_rel_url))  # send direct file
    elif fixed_rel_url is None:
        abort(404)  # relative url is invalid
    elif rel_url != fixed_rel_url:
        return redirect(url_for('.page', rel_url=fixed_rel_url))  # it's not the correct relative url, so redirect
    elif rel_url.endswith('/'):
        # try <rel_url>index.html
        rel_url_with_index = rel_url + 'index.html'
        _, exists = storage.fix_page_relative_url(rel_url_with_index)
        if exists:
            # send direct index.html
            return send_file(os.path.join(current_app.instance_path, 'pages', rel_url_with_index))

    page_ = storage.get_page(rel_url, include_draft=False)
    if page_ is None:
        abort(404)

    page_d = page_.to_dict()
    del page_d['raw_content']
    page_d['content'] = get_parser(page_.format).parse_whole(page_.raw_content)
    page_d['content'], toc, toc_html = parse_toc(page_d['content'])
    page_d['url'] = request.base_url
    page_ = page_d

    if page_['layout'] != 'page':
        return custom_render_template(page_['layout'] + '.html', entry=page_)
    return dict(entry=page_, toc=toc, toc_html=toc_html)


@templated('category.html', 'archive.html')
@cache.memoize(timeout=2 * 60)
def category(category_name):
    posts = storage.get_posts_with_limits(include_draft=False, **{'categories': [category_name]})
    if not posts:
        abort(404)

    def convert_to_dict(post_):
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_post_abs_url(post_.rel_url)
        return post_d

    posts = list(map(convert_to_dict, posts))
    return dict(entries=posts, archive_type='Category', archive_name=category_name)


@templated('tag.html', 'archive.html')
@cache.memoize(timeout=2 * 60)
def tag(tag_name):
    posts = storage.get_posts_with_limits(include_draft=False, **{'tags': [tag_name]})
    if not posts:
        abort(404)

    def convert_to_dict(post_):
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_post_abs_url(post_.rel_url)
        return post_d

    posts = list(map(convert_to_dict, posts))
    return dict(entries=posts, archive_type='Tag', archive_name=tag_name)


@templated('archive.html')
@cache.memoize(timeout=2 * 60)
def archive(year=None, month=None):
    posts = storage.get_posts_with_limits(include_draft=False)

    rel_url_prefix = ''
    archive_name = ''
    if year is not None:
        rel_url_prefix += '%04d/' % year
        archive_name += str(year)
    if month is not None:
        rel_url_prefix += '%02d/' % month
        archive_name += '.' + str(month)

    def convert_to_dict(post_):
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_post_abs_url(post_.rel_url)
        return post_d

    posts = list(map(convert_to_dict, filter(lambda p: p.rel_url.startswith(rel_url_prefix), posts)))
    return dict(entries=posts, archive_type='Archive', archive_name=archive_name if archive_name else 'All')


@templated('search.html', 'archive.html')
def search():
    raw_query = request.args.get('q', '').strip()
    query = raw_query.lower()
    if not query:
        abort(404)

    def process(p):
        del p['raw_content']
        p['url'] = make_post_abs_url(p['rel_url'])
        return p

    result = list(map(process, map(Base.to_dict, storage.search_for(query))))
    return dict(entries=result, archive_type='Search', archive_name='"{}"'.format(raw_query))


@cache.memoize(timeout=2 * 60)
def feed():
    def convert_to_dict(p):
        post_d = p.to_dict()
        del post_d['raw_content']
        post_d['content'] = get_parser(p.format).parse_whole(p.raw_content)
        post_d['url'] = make_post_abs_url(p.rel_url)
        return post_d

    posts = map(convert_to_dict, islice(storage.get_posts(include_draft=False), 0, current_app.config['FEED_COUNT']))
    fg = FeedGenerator()
    fg.id(request.url_root)
    if 'title' in site:
        fg.title(site['title'])
    if 'subtitle' in site:
        fg.subtitle(site['subtitle'])
    if 'language' in site:
        fg.language(site['language'])
    fg.author(dict(name=site.get('author', ''), email=site.get('email', '')))
    fg.link(href=request.url_root, rel='alternate')
    fg.link(href=url_for('.feed'), rel='self')
    for post_ in posts:
        fe = fg.add_entry()
        fe.id(post_['url'])
        fe.title(post_['title'])
        fe.published(post_['created'].replace(tzinfo=timezone_from_str(site.get('timezone', 'UTC+08:00'))))
        fe.updated(post_['updated'].replace(tzinfo=timezone_from_str(site.get('timezone', 'UTC+08:00'))))
        fe.link(href=make_post_abs_url(post_['rel_url']), rel='alternate')
        fe.author(dict(name=post_['author'], email=post_['email']))
        fe.content(post_['content'])

    atom_feed = fg.atom_str(pretty=True)
    response = make_response(atom_feed)
    response.content_type = 'application/atom+xml; charset=utf-8'
    return response

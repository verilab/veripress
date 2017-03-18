from itertools import islice

from feedgen.feed import FeedGenerator
from flask import url_for, request, redirect, current_app, send_file, abort, make_response

from veripress import site, cache
from veripress.view import templated, custom_render_template
from veripress.model import storage
from veripress.model.models import Base
from veripress.model.parsers import get_parser
from veripress.helpers import timezone_from_str, parse_toc

make_abs_url = lambda u: request.script_root + u  # 'u' means unique key


@cache.memoize(timeout=2 * 60)
@templated()
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
        post_d['url'] = make_abs_url(post_.unique_key)
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


@cache.memoize(timeout=2 * 60)
@templated()
def post(year, month, day, post_name):
    rel_url = request.path[len('/post/'):]
    fixed_rel_url = storage.fix_post_relative_url(rel_url)
    if rel_url != fixed_rel_url:
        return redirect(request.url_root + 'post/' + fixed_rel_url)  # it's not the correct relative url, so redirect

    post_ = storage.get_post(rel_url, include_draft=False)
    if post_ is None:
        abort(404)

    post_d = post_.to_dict()
    del post_d['raw_content']
    post_d['content'] = get_parser(post_.format).parse_whole(post_.raw_content)
    post_d['content'], post_d['toc'], post_d['toc_html'] = parse_toc(post_d['content'])
    post_d['url'] = make_abs_url(post_.unique_key)
    post_ = post_d

    return custom_render_template(post_['layout'] + '.html', entry=post_)


@templated()
def page(rel_url):
    fixed_rel_url, exists = storage.fix_page_relative_url(rel_url)
    if exists:
        file_path = fixed_rel_url
        return send_file(file_path)  # send direct file
    elif fixed_rel_url is None:  # relative url is invalid
        abort(404)  # pragma: no cover, this is never possible when visiting this site in web browser
    elif rel_url != fixed_rel_url:
        return redirect(url_for('.page', rel_url=fixed_rel_url))  # it's not the correct relative url, so redirect

    resp = cache.get('view-handler.' + rel_url)
    if resp is not None:
        return resp  # pragma: no cover, here just get the cached response

    page_ = storage.get_page(rel_url, include_draft=False)
    if page_ is None:
        abort(404)

    page_d = page_.to_dict()
    del page_d['raw_content']
    page_d['content'] = get_parser(page_.format).parse_whole(page_.raw_content)
    page_d['content'], page_d['toc'], page_d['toc_html'] = parse_toc(page_d['content'])
    page_d['url'] = make_abs_url(page_.unique_key)
    page_ = page_d

    resp = custom_render_template(page_['layout'] + '.html', entry=page_)
    cache.set('view-handler.' + rel_url, resp, timeout=2 * 60)
    return resp


@cache.memoize(timeout=2 * 60)
@templated('category.html', 'archive.html')
def category(category_name):
    posts = storage.get_posts_with_limits(include_draft=False, **{'categories': [category_name]})
    if not posts:
        abort(404)

    def convert_to_dict(post_):
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_abs_url(post_.unique_key)
        return post_d

    posts = list(map(convert_to_dict, posts))
    return dict(entries=posts, archive_type='Category', archive_name=category_name)


@cache.memoize(timeout=2 * 60)
@templated('tag.html', 'archive.html')
def tag(tag_name):
    posts = storage.get_posts_with_limits(include_draft=False, **{'tags': [tag_name]})
    if not posts:
        abort(404)

    def convert_to_dict(post_):
        post_d = post_.to_dict()
        del post_d['raw_content']
        post_d['preview'], post_d['has_more_content'] = get_parser(post_.format).parse_preview(post_.raw_content)
        post_d['url'] = make_abs_url(post_.unique_key)
        return post_d

    posts = list(map(convert_to_dict, posts))
    return dict(entries=posts, archive_type='Tag', archive_name=tag_name)


@cache.memoize(timeout=2 * 60)
@templated()
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
        post_d['url'] = make_abs_url(post_.unique_key)
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
        p['url'] = make_abs_url(p['unique_key'])
        return p

    result = list(map(process, map(Base.to_dict, storage.search_for(query))))
    return dict(entries=result, archive_type='Search', archive_name='"{}"'.format(raw_query))


@cache.memoize(timeout=2 * 60)
def feed():
    def convert_to_dict(p):
        post_d = p.to_dict()
        del post_d['raw_content']
        post_d['content'] = get_parser(p.format).parse_whole(p.raw_content)
        post_d['url'] = make_abs_url(p.unique_key)
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
        fe.link(href=make_abs_url(post_['unique_key']), rel='alternate')
        fe.author(dict(name=post_['author'], email=post_['email']))
        fe.content(post_['content'])

    atom_feed = fg.atom_str(pretty=True)
    response = make_response(atom_feed)
    response.content_type = 'application/atom+xml; charset=utf-8'
    return response

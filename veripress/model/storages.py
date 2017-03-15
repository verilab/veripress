import re
import os
import functools
from datetime import date, datetime, timedelta

import yaml
from flask import current_app

from veripress.model.models import Page, Post, Widget
from veripress.model.parsers import get_standard_format_name
from veripress.helpers import to_list, to_datetime, Pair, traverse_directory


class Storage(object):
    def __init__(self, config):
        """
        Save the configurations and initialize attributes.

        :param config: configuration, typically the Flask app's config
        """
        self.config = config
        self._closed = False

    def close(self):
        """
        Close the storage.
        Subclasses should override this to close any file descriptor or database connection if necessary.
        """
        self._closed = True

    @property
    def closed(self):
        """
        Read-only property.
        This state should be changed only in 'close' method.
        """
        return self._closed

    def fix_relative_url(self, publish_type, rel_url):
        """
        Fix post or page relative url to a standard, uniform format.

        :param publish_type: publish type ('post' or 'page')
        :param rel_url: relative url to fix
        :return: tuple(fixed relative url or None if cannot recognize, file exists or not)
        :raise ValueError: unknown publish type
        """
        if publish_type == 'post':
            return self.fix_post_relative_url(rel_url), False
        elif publish_type == 'page':
            return self.fix_page_relative_url(rel_url)
        else:
            raise ValueError('Publish type "{}" is not supported'.format(publish_type))

    @staticmethod
    def fix_post_relative_url(rel_url):
        """
        Fix post relative url to a standard, uniform format.

        Possible input:
        - 2016/7/8/my-post
        - 2016/07/08/my-post.html
        - 2016/8/09/my-post/
        - 2016/8/09/my-post/index
        - 2016/8/09/my-post/index.htm
        - 2016/8/09/my-post/index.html

        :param rel_url: relative url to fix
        :return: fixed relative url, or None if cannot recognize
        """
        m = re.match(
            '^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<post_name>[^/]+?)'
            '(?:(?:\.html)|(?:/(?P<index>index(?:\.html?)?)?))?$',
            rel_url
        )
        if not m:
            return None

        year, month, day, post_name = m.groups()[:4]
        try:
            d = date(year=int(year), month=int(month), day=int(day))
            return '/'.join((d.strftime('%Y/%m/%d'), post_name, 'index.html' if m.group('index') else ''))
        except (TypeError, ValueError):
            # the date is invalid
            return None

    @staticmethod
    def fix_page_relative_url(rel_url):
        """
        Fix page relative url to a standard, uniform format.

        Possible input:
        - my-page
        - my-page/
        - my-page/index
        - my-page/index.htm
        - my-page/index.html
        - my-page/specific.file

        NOTE!
        Because custom page has a very strong connection with the storage type chosen,
        this method should be implemented in subclasses.

        :param rel_url: relative url to fix
        :return: tuple(fixed relative url or None if cannot recognize, file exists or not)
        """
        raise NotImplementedError

    def get_posts(self, include_draft=False, filter_functions=None):
        """Get all posts, returns an iterable of Post object."""
        raise NotImplementedError

    def get_post(self, rel_url, include_draft=False):
        """Get post for given relative url, returns a Post object."""
        raise NotImplementedError

    def get_tags(self):
        """Get all tags as a dict (key: tag_name, value: Pair(count_all, count_published))."""
        raise NotImplementedError

    def get_categories(self):
        """Get all categories as a dict. (key: category_name, value: Pair(count_all, count_published))."""
        raise NotImplementedError

    def get_pages(self, include_draft=False):
        """Get all custom pages, returns an iterable of Page object."""
        raise NotImplementedError

    def get_page(self, rel_url, include_draft=False):
        """Get custom page for given relative url, returns a Page object."""
        raise NotImplementedError

    def get_widgets(self, position=None, include_draft=False):
        """Get all widgets, returns an iterable of Widget object."""
        raise NotImplementedError

    @staticmethod
    def _filter_result(result, filter_functions=None):
        """
        Filter result with given filter functions.

        :param result: an iterable object
        :param filter_functions: some filter functions
        :return: a filter object (filtered result)
        """
        if filter_functions is not None:
            for filter_func in filter_functions:
                result = filter(filter_func, result)
        return result

    def get_posts_with_limits(self, include_draft=False, **limits):
        """
        Get all posts and filter them as needed.

        :param include_draft: return draft posts or not
        :param limits: other limits to the attrs of the result, should be a dict with string or list values
        :return: an iterable of Post objects
        """
        filter_funcs = []

        for attr in ('title', 'layout', 'author', 'email', 'tags', 'categories'):
            if limits.get(attr):
                filter_set = set(to_list(limits.get(attr)))

                def get_filter_func(filter_set_, attr_):
                    return lambda p: filter_set_.intersection(to_list(getattr(p, attr_)))

                filter_funcs.append(get_filter_func(filter_set, attr))

        for attr in ('created', 'updated'):
            interval = limits.get(attr)
            if isinstance(interval, (list, tuple)) and len(interval) == 2 \
                    and isinstance(interval[0], date) and isinstance(interval[1], date):
                # [start date(time), end date(time)]
                start, end = interval
                start = to_datetime(start)
                if not isinstance(end, datetime):
                    # 'end' is a date, we should convert it to 00:00:00 of the next day,
                    # so that posts of that day will be included
                    end = datetime.strptime('%04d-%02d-%02d' % (end.year, end.month, end.day), '%Y-%m-%d')
                    end += timedelta(days=1)

                def get_filter_func(attr_, start_dt, end_dt):
                    return lambda p: start_dt < getattr(p, attr_) < end_dt

                filter_funcs.append(get_filter_func(attr, start, end))

        return self.get_posts(include_draft=include_draft, filter_functions=filter_funcs)


class FileStorage(Storage):
    @staticmethod
    def fix_page_relative_url(rel_url):
        """
        Fix page relative url to a standard, uniform format.

        Possible input:
        - my-page
        - my-page/
        - my-page/index
        - my-page/index.htm
        - my-page/index.html
        - my-page/specific.file

        :param rel_url: relative url to fix
        :return: tuple(fixed relative url or None if cannot recognize, file exists or not)
        """
        rel_url = rel_url.lstrip('/')  # trim all heading '/'
        endswith_slash = rel_url.endswith('/')
        rel_url = rel_url.rstrip('/') + ('/' if endswith_slash else '')  # preserve only one trailing '/'
        if not rel_url or rel_url == '/':
            return None, False

        file_path = os.path.join(current_app.instance_path, 'pages', rel_url.replace('/', os.path.sep))
        if rel_url.endswith('/'):
            return rel_url, False
        elif os.path.isfile(file_path):
            return rel_url, True
        elif os.path.isdir(file_path):
            return rel_url + '/', False
        else:
            sp = rel_url.rsplit('/', 1)
            m = re.match('(.+)\.html?', sp[-1])
            if m:
                sp[-1] = m.group(1) + '.html'
            else:
                sp[-1] += '.html'
            return '/'.join(sp), False

    @staticmethod
    def search_file(search_root, search_filename, instance_relative_root=False):
        """
        Search for a filename in a specific search root dir.

        :param search_root: root dir to search
        :param search_filename: filename to search (no extension)
        :param instance_relative_root: search root is relative to instance path or not
        :return: tuple(full_file_path, extension without heading dot)
        """
        if instance_relative_root:
            search_root = os.path.join(current_app.instance_path, search_root)
        file_path = None
        file_ext = None
        for file in os.listdir(search_root):
            filename, ext = os.path.splitext(file)
            if filename == search_filename and ext and ext != '.':
                file_path = os.path.join(search_root, filename + ext)
                file_ext = ext[1:]  # remove heading '.' (dot)
                break
        return file_path, file_ext

    # noinspection PyUnresolvedReferences
    search_instance_file = staticmethod(functools.partial(search_file.__func__, instance_relative_root=True))

    @staticmethod
    def read_file(file_path):
        """
        Read yaml head and raw body content from a file.

        :param file_path: file path
        :return: tuple(meta, raw_content)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            whole = f.read().strip()

        if whole.startswith('---'):
            # may has yaml meta info, so we try to split it out
            sp = re.split('-{3,}', whole.lstrip('-'), maxsplit=1)
            if len(sp) == 2:
                # do have yaml meta info, so we read it
                return yaml.load(sp[0]), sp[1].lstrip()
        return {}, whole

    def get_posts(self, include_draft=False, filter_functions=None):
        """
        Get all posts from filesystem.

        :param include_draft: return draft posts or not
        :param filter_functions: filter functions to apply BEFORE result being sorted
        :return: an iterable of Post objects (the first is the latest post)
        """

        def posts_generator(path):
            """Loads valid posts one by one in the given path."""
            if os.path.isdir(path):
                for file in os.listdir(path):
                    filename, ext = os.path.splitext(file)
                    format_name = get_standard_format_name(ext[1:])
                    if format_name is not None and re.match('\d{4}-\d{2}-\d{2}-.+', filename):
                        # the format is supported and the filename is valid, so load this post
                        post = Post()
                        post.format = format_name
                        post.meta, post.raw_content = FileStorage.read_file(os.path.join(path, file))
                        post.rel_url = filename.replace('-', '/', 3) + '/'
                        post.unique_key = '/' + post.rel_url
                        yield post

        posts_path = os.path.join(current_app.instance_path, 'posts')
        result = filter(lambda p: include_draft or not p.is_draft, posts_generator(posts_path))
        result = self._filter_result(result, filter_functions)

        return sorted(result, key=lambda p: p.created, reverse=True)

    def get_post(self, rel_url, include_draft=False):
        """
        Get post for given relative url from filesystem.

        Possible input:
        - 2017/01/01/my-post/
        - 2017/01/01/my-post/index.html

        :param rel_url: relative url
        :param include_draft: return draft post or not
        :return: a Post object
        """
        raw_rel_url = str(rel_url)
        if rel_url.endswith('/index.html'):
            rel_url = rel_url.rsplit('/', 1)[0] + '/'  # remove the trailing 'index.html'
        post_filename = rel_url[:-1].replace('/', '-')

        post_file_path, post_file_ext = FileStorage.search_instance_file('posts', post_filename)
        if post_file_path is None or post_file_ext is None:
            # no such post
            return None

        # construct the post object
        post = Post()
        post.rel_url = raw_rel_url
        post.unique_key = '/post/' + rel_url  # 'rel_url' contains no trailing 'index.html'
        post.format = get_standard_format_name(post_file_ext)
        post.meta, post.raw_content = FileStorage.read_file(post_file_path)
        return post if include_draft or not post.is_draft else None

    def get_tags(self):
        """
        Get all tags and post count of each tag.

        :return: dict_item(tag_name, Pair(count_all, count_published))
        """
        posts = self.get_posts(include_draft=True)
        result = {}
        for post in posts:
            for tag_name in set(post.tags):
                result[tag_name] = result.setdefault(tag_name, Pair(0, 0)) + Pair(1, 0 if post.is_draft else 1)
        return result.items()

    def get_categories(self):
        """
        Get all categories and post count of each category.

        :return dict_item(category_name, Pair(count_all, count_published))
        """
        posts = self.get_posts(include_draft=True)
        result = {}
        for post in posts:
            for category_name in set(post.categories):
                result[category_name] = result.setdefault(category_name, Pair(0, 0)) \
                                        + Pair(1, 0 if post.is_draft else 1)
        return result.items()

    def get_pages(self, include_draft=False):
        """
        Get all custom pages (supported formats, excluding other files like '.js', '.css', '.html').

        :param include_draft: return draft page or not
        :return: an iterable of Page objects
        """

        def pages_generator(pages_root_path):
            for file_path in traverse_directory(pages_root_path, yield_dir=False):
                rel_path = os.path.relpath(file_path, pages_root_path)
                rel_path, ext = os.path.splitext(rel_path)
                if not ext or ext == '.' or get_standard_format_name(ext[1:]) is None:
                    continue  # pragma: no cover, it seems that coverage cannot recognize this line

                if rel_path.endswith('/index'):
                    rel_path = rel_path[:-len('index')]
                else:
                    rel_path += '.html'
                page = self.get_page(rel_path.replace(os.path.sep, '/'), include_draft=include_draft)
                if page is not None:
                    yield page

        pages_path = os.path.join(current_app.instance_path, 'pages')
        return pages_generator(pages_path)

    def get_page(self, rel_url, include_draft=False):
        """
        Get custom page for given relative url from filesystem.

        Possible input:
        - my-page/
        - my-page/index.html
        - my-another-page.html
        - a/b/c/
        - a/b/c/d.html

        :param rel_url: relative url
        :param include_draft: return draft page or not
        :return: a Page object
        """
        page_dir = os.path.dirname(rel_url.replace('/', os.path.sep))
        page_path = os.path.join(current_app.instance_path, 'pages', page_dir)
        if not os.path.isdir(page_path):
            # no such directory
            return None

        page_filename = rel_url[len(page_dir):].lstrip('/')
        if not page_filename:
            page_filename = 'index'
        else:
            page_filename = os.path.splitext(page_filename)[0]

        page_file_path, page_file_ext = FileStorage.search_file(page_path, page_filename)
        if page_file_path is None or page_file_ext is None:
            # no such page
            return None

        page = Page()
        page.rel_url = rel_url
        page.unique_key = '/' + (rel_url.rsplit('/', 1)[0] + '/' if rel_url.endswith('/index.html') else rel_url)
        page.format = get_standard_format_name(page_file_ext)
        page.meta, page.raw_content = FileStorage.read_file(page_file_path)
        return page if include_draft or not page.is_draft else None

    def get_widgets(self, position=None, include_draft=False):
        """
        Get widgets for given position from filesystem.

        :param position: position or position list
        :param include_draft: return draft widgets or not
        :return: an iterable of Widget objects
        """

        def widgets_generator(path):
            """Loads valid widgets one by one in the given path."""
            if os.path.isdir(path):
                for file in os.listdir(path):
                    _, ext = os.path.splitext(file)
                    format_name = get_standard_format_name(ext[1:])
                    if format_name is not None:
                        # the format is supported, so load it
                        widget = Widget()
                        widget.format = format_name
                        widget.meta, widget.raw_content = FileStorage.read_file(os.path.join(path, file))
                        yield widget

        widgets_path = os.path.join(current_app.instance_path, 'widgets')
        positions = to_list(position) if position is not None else position
        result = filter(lambda w: (w.position in positions if positions is not None else True)
                                  and (include_draft or not w.is_draft),
                        widgets_generator(widgets_path))
        return sorted(result, key=lambda w: (w.position, w.order))

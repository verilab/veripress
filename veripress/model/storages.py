import re
import os
from datetime import date

import yaml
from flask import current_app

from veripress.model.models import Page, Post, Widget
from veripress.model.parsers import get_standard_format_name


class Storage(object):
    def __init__(self, config):
        self.config = config
        self.closed = False

    def close(self):
        """
        Close the storage.
        Subclasses should override this to close any file descriptor or database connection if necessary.
        """
        self.closed = True

    @staticmethod
    def fix_relative_url(publish_type, rel_url):
        """
        Fix post or page relative url to a standard, uniform format.

        :param publish_type: publish type ('post' or 'page')
        :param rel_url: relative url to fix
        :return: tuple(fixed relative url or None if cannot recognize, file exists or not)
        :raise ValueError: unknown publish type
        """
        if publish_type == 'post':
            return Storage.fix_post_relative_url(rel_url), False
        elif publish_type == 'page':
            return Storage.fix_page_relative_url(rel_url)
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
            '^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<post_name>[^/]+)/?(?P<index>index(?:\.html?)?)?$',
            rel_url
        )
        if not m:
            return None

        year, month, day, post_name = m.groups()[:4]
        try:
            d = date(year=int(year), month=int(month), day=int(day))
            return '/'.join([d.strftime('%Y/%m/%d'), post_name, 'index.html' if m.group('index') else ''])
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

    def get_posts(self):
        """Get all posts, returns an iterable object."""
        raise NotImplementedError

    def get_post(self, rel_url):
        """Get post for given relative url, returns a post model object."""
        raise NotImplementedError

    def get_page(self, rel_url):
        """Get custom page for given relative url, returns a custom page model object."""
        raise NotImplementedError

    def get_widgets(self, position=None):
        """Get all widgets, returns an iterable object."""
        raise NotImplementedError


class FileStorage(Storage):
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

    @staticmethod
    def search_file(search_root, search_filename):
        """
        Search for a filename in a specific search root dir.

        :param search_root: root dir to search
        :param search_filename: filename to search (no extension)
        :return: tuple(full_file_path, extension without heading dot)
        """
        file_path = None
        file_ext = None
        for file in os.listdir(search_root):
            filename, ext = os.path.splitext(file)
            if filename == search_filename and ext and ext != '.':
                file_path = os.path.join(search_root, filename + ext)
                file_ext = ext[1:]  # remove heading '.' (dot)
                break
        return file_path, file_ext

    def get_posts(self):
        pass

    def get_post(self, rel_url):
        """
        Get post for given relative url from filesystem.

        Possible input:
        - 2017/01/01/my-post/
        - 2017/01/01/my-post/index.html

        :param rel_url: relative url
        :return: a Post object
        """
        raw_rel_url = str(rel_url)
        if rel_url.endswith('/index.html'):
            rel_url = rel_url.rsplit('/', 1)[0] + '/'  # remove the trailing 'index.html'
        post_filename = rel_url[:-1].replace('/', '-')
        posts_path = os.path.join(current_app.instance_path, 'posts')

        post_file_path, post_file_ext = FileStorage.search_file(posts_path, post_filename)
        if post_file_path is None or post_file_ext is None:
            # no such post
            return None

        # construct the post object
        post = Post()
        post.rel_url = raw_rel_url
        post.unique_key = '/post/' + rel_url  # 'rel_url' contains no trailing 'index.html'
        post.format = get_standard_format_name(post_file_ext)
        post.meta, post.raw_content = FileStorage.read_file(post_file_path)
        return post

    def get_page(self, rel_url):
        """
        Get custom page for given relative url from filesystem.

        Possible input:
        - my-page/
        - my-page/index.html
        - my-another-page.html
        - a/b/c/
        - a/b/c/d.html

        :param rel_url: relative url
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
        return page

    def get_widgets(self, position=None):
        pass

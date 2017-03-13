import os
from datetime import datetime, date

from flask import current_app

from veripress import app
from veripress.model import storage
from veripress.model.models import Page, Post, Widget
from veripress.model.storages import FileStorage


def test_read_file():
    with app.app_context():
        file_path = os.path.join(current_app.instance_path, 'posts', '2017-03-09-my-post.txt')
        meta = {
            'created': date(year=2017, month=3, day=9),
            'updated': datetime.strptime('2017-03-10 10:24:00', '%Y-%m-%d %H:%M:%S'),
            'categories': ['Default'],
            'tags': 'Hello World'
        }
        raw_content = 'Lorem ipsum dolor sit amet.'
        assert (meta, raw_content) == FileStorage.read_file(file_path)

        file_path = os.path.join(current_app.instance_path, 'posts', '2017-03-09-my-post-no-yaml.txt')
        meta = {}
        assert (meta, raw_content) == FileStorage.read_file(file_path)

        file_path = os.path.join(current_app.instance_path, 'posts', '2017-03-09-my-post-no-yaml2.txt')
        raw_content = '---\n\nLorem ipsum dolor sit amet.'
        assert (meta, raw_content) == FileStorage.read_file(file_path)


def test_search_file():
    with app.app_context():
        search_root = os.path.join(current_app.instance_path, 'posts')
        path, ext = FileStorage.search_file(search_root, '2017-03-09-my-post')
        assert path == os.path.join(search_root, '2017-03-09-my-post.txt')
        assert ext == 'txt'

        search_root = 'posts'
        path, ext = FileStorage.search_file(search_root, '2017-03-09-my-post', instance_relative_root=True)
        assert (path, ext) == FileStorage.search_instance_file(search_root, '2017-03-09-my-post')
        assert path == os.path.join(current_app.instance_path, search_root, '2017-03-09-my-post.txt')
        assert ext == 'txt'


def test_get_post():
    with app.app_context():
        post = storage.get_post('2017/03/09/my-post/index.html')
        assert isinstance(post, Post)
        assert post.rel_url == '2017/03/09/my-post/index.html'
        assert post.unique_key == '/post/2017/03/09/my-post/'  # unique_key has no trailing 'index.html'
        assert post.format == 'txt'
        assert (post.meta, post.raw_content) == FileStorage.read_file(
            os.path.join(current_app.instance_path, 'posts', '2017-03-09-my-post.txt')
        )

        post = storage.get_post('2017/03/09/my-post-no-yaml/')
        assert post.rel_url == '2017/03/09/my-post-no-yaml/'
        assert post.unique_key == '/post/2017/03/09/my-post-no-yaml/'
        assert post.format == 'txt'

        post = storage.get_post('2016/03/03/hello-world/')
        assert post is None
        post = storage.get_post('2016/03/03/hello-world/', include_draft=True)
        assert post is not None

        post = storage.get_post('2016/03/03/non-exists/')
        assert post is None


def test_get_page():
    with app.app_context():
        page = storage.get_page('my-page/')
        assert isinstance(page, Page)
        assert page.rel_url == 'my-page/'
        assert page.unique_key == '/my-page/'
        assert page.format == 'markdown'
        assert (page.meta, page.raw_content) == FileStorage.read_file(
            os.path.join(current_app.instance_path, 'pages', 'my-page', 'index.md')
        )

        page = storage.get_page('my-page/index.html')
        assert page.rel_url == 'my-page/index.html'
        assert page.unique_key == '/my-page/'
        assert page.format == 'markdown'

        page = storage.get_page('index.html')
        assert page.rel_url == 'index.html'
        assert page.unique_key == '/index.html'
        assert page.format == 'markdown'

        page = storage.get_page('test-page.html')
        assert page.rel_url == 'test-page.html'
        assert page.unique_key == '/test-page.html'
        assert page.format == 'txt'

        page = storage.get_page('test-page-draft.html')
        assert page is None
        page = storage.get_page('test-page-draft.html', include_draft=True)
        assert page is not None

        page = storage.get_page('test-non-exists.html')
        assert page is None
        page = storage.get_page('non-exists/non-exists.html')
        assert page is None


def test_get_widgets():
    with app.app_context():
        widgets = storage.get_widgets()
        assert isinstance(widgets, list)
        assert len(widgets) == 2
        assert isinstance(widgets[0], Widget)
        assert widgets[0].position == widgets[1].position
        assert widgets[0].order < widgets[1].order

        widgets = storage.get_widgets(position='header', include_draft=True)
        assert len(list(widgets)) == 1

        widgets = storage.get_widgets(position='non-exists', include_draft=True)
        assert len(list(widgets)) == 0


def test_get_posts():
    with app.app_context():
        posts = storage.get_posts()
        assert isinstance(posts, list)
        assert len(posts) == 3

        posts = storage.get_posts(include_draft=True)
        assert len(posts) == 4
        assert posts[-1].title == 'Hello, world!'
        assert posts[-1].is_draft == True

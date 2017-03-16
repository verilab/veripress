from datetime import date, datetime
from collections import Iterable

from pytest import raises

from veripress import app, create_app
from veripress.model import storage, get_storage
from veripress.model.storages import Storage, FileStorage
from veripress.helpers import ConfigurationError


def test_get_storage():
    wrong_app = create_app('config2.py')
    assert wrong_app.config['STORAGE_TYPE'] == 'fake_type'
    with raises(ConfigurationError, message='Storage type "fake_type" is not supported.'):
        with wrong_app.app_context():
            get_storage()  # this will raise a ConfigurationError, because the storage type is not supported

    with app.app_context():
        s = get_storage()
        assert storage == s
        assert id(storage) != id(s)
        # noinspection PyProtectedMember
        assert storage._get_current_object() == s

        assert isinstance(s, Storage)
        assert isinstance(s, FileStorage)
        assert s.config['STORAGE_TYPE'] == 'file'
    assert s.closed  # the storage object should be marked as 'closed' after the app context being torn down
    with raises(AttributeError):
        setattr(s, 'closed', True)


def test_fix_rel_url():
    with app.app_context():
        correct = '2017/01/01/my-post/'
        assert Storage.fix_post_relative_url('2017/01/01/my-post/') == correct
        assert Storage.fix_post_relative_url('2017/1/1/my-post') == correct
        assert Storage.fix_post_relative_url('2017/1/1/my-post.html') == correct
        assert Storage.fix_post_relative_url('2017/1/1/my-post/index') == correct + 'index.html'
        assert Storage.fix_post_relative_url('2017/1/1/my-post/index.html') == correct + 'index.html'
        assert Storage.fix_post_relative_url('2017/1/1/my-post/test') is None
        assert Storage.fix_post_relative_url('2017/13/32/my-post/') is None

        # assert Storage.fix_page_relative_url('my-page') == ('my-page/', False)
        # assert Storage.fix_page_relative_url('my-page/') == ('my-page/', False)
        # assert Storage.fix_page_relative_url('test-page.txt') == ('test-page.txt', True)
        # assert Storage.fix_page_relative_url('my-page/index.md') == ('my-page/index.md', True)
        # assert Storage.fix_page_relative_url('my-page/index') == ('my-page/index.html', False)
        # assert Storage.fix_page_relative_url('my-page/index.htm') == ('my-page/index.html', False)
        # assert Storage.fix_page_relative_url('my-page/index.html') == ('my-page/index.html', False)
        # assert Storage.fix_page_relative_url('//') == (None, False)

        storage_ = Storage({})
        assert storage_.fix_relative_url('post', '2017/1/1/my-post/index') == ('2017/01/01/my-post/index.html', False)
        # assert Storage.fix_relative_url('page', '/my-page/index.htm') == ('my-page/index.html', False)
        with raises(ValueError, message='Publish type "wrong" is not supported'):
            storage_.fix_relative_url('wrong', 'wrong-publish-type/')


def test_base_storage():
    s = Storage(app.config)
    with raises(NotImplementedError):
        s.fix_page_relative_url('')
    with raises(NotImplementedError):
        s.get_posts()
    with raises(NotImplementedError):
        s.get_post('')
    with raises(NotImplementedError):
        s.get_tags()
    with raises(NotImplementedError):
        s.get_categories()
    with raises(NotImplementedError):
        s.get_pages()
    with raises(NotImplementedError):
        s.get_page('')
    with raises(NotImplementedError):
        s.get_widgets()


def test_get_posts_with_limits():
    with app.app_context():
        posts = storage.get_posts_with_limits(include_draft=True)
        assert posts == storage.get_posts(include_draft=True)

        posts = storage.get_posts_with_limits(include_draft=True, tags='Hello World', categories=['Default'])
        assert len(posts) == 2

        posts = storage.get_posts_with_limits(include_draft=True,
                                              created=(datetime.strptime('2016-02-02', '%Y-%m-%d'),
                                                       date(year=2016, month=3, day=3)))
        assert len(posts) == 1

        posts = storage.get_posts_with_limits(include_draft=True,
                                              created=(date(year=2011, month=2, day=2),
                                                       date(year=2014, month=2, day=2)))
        assert len(posts) == 0


def test_search_for():
    with app.app_context():
        assert storage.search_for('') == []
        assert isinstance(storage.search_for('Hello'), Iterable)
        assert len(list(storage.search_for('Hello'))) == 1
        assert len(list(storage.search_for('Hello', include_draft=True))) == 2

    app.config['ALLOW_SEARCH_PAGES'] = False
    with app.app_context():
        assert len(list(storage.search_for('Hello'))) == 0
    app.config['ALLOW_SEARCH_PAGES'] = True

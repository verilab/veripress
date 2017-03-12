import json
from datetime import datetime, timedelta, date

from pytest import raises

from veripress import app
from veripress.model import CustomJSONEncoder
from veripress.model.models import Base, Page, Post, Widget


def test_base_model():
    base = Base()
    assert base.meta == {}

    base.format = 'TXT'
    assert base.format == 'txt'  # the 'format' property automatically convert the value to lowercase

    base.meta = {'title': 'Hello world', 'author': 'Richard'}
    base.raw_content = 'This is a test content'
    assert base.is_draft == False  # default value is False
    assert base.to_dict() == {
        'meta': {'title': 'Hello world', 'author': 'Richard'},
        'format': 'txt',
        'raw_content': 'This is a test content',
        'is_draft': False
    }

    base.meta['is_draft'] = True
    assert base.is_draft == True  # will change dynamically when meta changes


def test_page_model():
    page = Page()
    assert page.layout == 'page'  # default layout
    assert page.title is None
    assert page.author == 'My Name'  # default value is from site.json
    assert page.email == 'my-email@example.com'  # like above
    assert page.created is None and page.updated is None

    assert hasattr(page, 'unique_key')
    assert hasattr(page, 'rel_url')

    dt = datetime.now()
    page.meta = {
        'author': 'Richard',
        'email': 'richard@example.com',
        'created': dt
    }
    assert page.author == 'Richard'
    assert page.email == 'richard@example.com'
    assert page.created == page.updated == dt

    # test parsing default title from rel_url
    page.rel_url = 'index.html'
    assert page.title == 'Index'
    page.rel_url = 'a-test-/index.html'
    assert page.title == 'A Test'
    page.rel_url = 'a--test/b-test/c-test.html'
    assert page.title == 'C Test'
    page.rel_url = 'a-test/b-test/'
    assert page.title == 'B Test'
    page.rel_url = '测试/index.html'
    assert page.title == '测试'

    page.meta['title'] = 'My Page'
    assert page.title == 'My Page'

    dt2 = datetime.now() + timedelta(days=2)
    page.meta['updated'] = dt2
    assert page.created != page.updated


def test_post_model():
    post = Post()
    assert isinstance(post, Page)

    # test parsing default title and created date from rel_url
    post.rel_url = '2017/03/10/my-post/'
    assert post.created == datetime.strptime('2017/03/10', '%Y/%m/%d')
    assert post.title == 'My Post'
    post.meta['title'] = 'My First Post'
    assert post.title == 'My First Post'

    # test tags and categories with str and list types
    assert post.tags == []
    assert post.categories == []
    post.meta['tags'] = 'VeriPress'
    assert post.tags == ['VeriPress']
    post.meta['categories'] = 'Dev'
    assert post.categories == ['Dev']

    post.meta['tags'] = ['A', 'B']
    assert post.tags == ['A', 'B']
    post.meta['categories'] = ['A']
    assert post.categories == ['A']


def test_widget_model():
    widget = Widget()
    assert widget.position is None
    assert widget.order is None
    assert not hasattr(widget, 'unique_key')
    assert not hasattr(widget, 'rel_url')
    assert isinstance(widget, Base)
    assert not isinstance(widget, Page)

    widget.meta['position'] = 'sidebar'
    widget.meta['order'] = 0
    assert widget.position == 'sidebar'
    assert widget.order == 0


def test_json_encoder():
    assert app.json_encoder == CustomJSONEncoder

    page = Page()
    page.rel_url = 'my-page/index.html'
    page.unique_key = '/my-page/'
    page.raw_content = 'This is the raw content.'
    page.format = 'txt'
    dt = datetime.now()
    page.meta = {'title': 'My Page', 'author': 'Richard', 'created': dt}
    result = json.dumps(page, cls=CustomJSONEncoder)
    assert json.loads(result) == {
        'meta': {'title': 'My Page', 'author': 'Richard', 'created': dt.timestamp()},
        'raw_content': 'This is the raw content.',
        'format': 'txt',
        'is_draft': False,
        'unique_key': '/my-page/',
        'rel_url': 'my-page/index.html',
        'layout': 'page',
        'title': 'My Page',
        'author': 'Richard',
        'email': 'my-email@example.com',
        'created': dt.timestamp(),
        'updated': dt.timestamp()
    }

    class NotSupportedClass:
        pass

    not_supported = NotSupportedClass()
    with raises(TypeError):
        json.dumps(not_supported, cls=CustomJSONEncoder)

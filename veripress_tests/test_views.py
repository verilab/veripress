from pytest import raises
from werkzeug.exceptions import NotFound

from veripress import app
from veripress.view import views


def test_404():
    with app.test_client() as c:
        resp = c.get('/non-exists.html')
        assert 'Page Not Found' in resp.data.decode('utf-8')


def test_index():
    with app.test_client() as c:
        assert c.get('/page/1').headers['Location'] == 'http://localhost/page/1/'
        assert c.get('/page/1/').headers['Location'] == 'http://localhost/'

        resp = c.get('/')
        assert resp.status_code == 200
        assert 'My Blog' in resp.data.decode('utf-8')
        assert '<a id="prev-url"' in resp.data.decode('utf-8')
        assert '<a id="next-url"' not in resp.data.decode('utf-8')
        assert 'My Post No Yaml' in resp.data.decode('utf-8')
        assert 'My Post No Yaml2' in resp.data.decode('utf-8')
        assert 'This is my blog. Welcome!' in resp.data.decode('utf-8')  # parse widget in template

        assert '<a id="next-url"' in c.get('/page/2/').data.decode('utf-8')


def test_post():
    with app.test_client() as c:
        resp = c.get('/post/2017/3/9/my-post')
        assert resp.headers['Location'].endswith('/2017/03/09/my-post/')

        resp = c.get('/post/2017/03/09/my-post/')
        assert 'My Post - My Blog' in resp.data.decode('utf-8')
        assert '<p>TOC</p>' in resp.data.decode('utf-8')
        assert '<p>TOC HTML</p>' in resp.data.decode('utf-8')

        resp = c.get('/post/2017/03/09/non-exists/')
        assert 'Page Not Found' in resp.data.decode('utf-8')

    app.config['SHOW_TOC'] = False
    with app.test_client() as c:
        resp = c.get('/post/2017/03/09/my-post/')
        assert 'My Post - My Blog' in resp.data.decode('utf-8')
        assert '<p>TOC</p>' not in resp.data.decode('utf-8')
        assert '<p>TOC HTML</p>' not in resp.data.decode('utf-8')
    app.config['SHOW_TOC'] = True


def test_page():
    with app.test_client() as c:
        resp = c.get('/abc')
        assert resp.status_code == 302
        assert resp.headers.get('Location').endswith('/abc.html')
        resp = c.get('/a/b')
        assert resp.status_code == 302
        assert resp.headers.get('Location').endswith('/a/b/')

        resp = c.get('/test-page.txt')
        assert resp.content_type == 'text/plain; charset=utf-8'

        resp = c.get('/dddd/')
        assert '<title>D</title>' in resp.data.decode('utf-8')

        resp = c.get('/test-page.html')
        assert 'Test Page' in resp.data.decode('utf-8')


def test_tags_categories_archive_search():
    with app.test_client() as c:
        resp = c.get('/tag/non-exists/')
        assert 'Page Not Found' in resp.data.decode('utf-8')
        resp = c.get('/category/non-exists/')
        assert 'Page Not Found' in resp.data.decode('utf-8')

        resp = c.get('/tag/Hello World/')
        assert 'Hello World - Tag - My Blog' in resp.data.decode('utf-8')
        assert 'My Post' in resp.data.decode('utf-8')

        resp = c.get('/category/Default/')
        assert 'Default - Category - My Blog' in resp.data.decode('utf-8')
        assert 'My Post' in resp.data.decode('utf-8')

        resp = c.get('/archive/2017/3/')
        assert '2017.3 - Archive - My Blog' in resp.data.decode('utf-8')
        assert 'My Post' in resp.data.decode('utf-8')

        resp = c.get('/search?q=')
        assert 'Page Not Found' in resp.data.decode('utf-8')
        resp = c.get('/search?q=no yaml')
        assert '&#34;no yaml&#34; - Search - My Blog' in resp.data.decode('utf-8')
        assert 'My Post No Yaml' in resp.data.decode('utf-8')
        resp = c.get('/search?q=Title')
        assert '&#34;Title&#34; - Search - My Blog' in resp.data.decode('utf-8')
        assert 'My Post No Yaml' not in resp.data.decode('utf-8')
        assert 'My Post' in resp.data.decode('utf-8')


def test_feed():
    with app.test_client() as c:
        resp = c.get('/feed.xml')
        assert 'My Post' in resp.data.decode('utf-8')
        assert 'My Post No Yaml' in resp.data.decode('utf-8')
        assert 'My Post No Yaml2' in resp.data.decode('utf-8')
        assert resp.content_type == 'application/atom+xml; charset=utf-8'

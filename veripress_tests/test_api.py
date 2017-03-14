import json

from flask import make_response, jsonify, Response
from pytest import raises

from veripress import app, site
from veripress.api import Error, json_api, ApiException


def get_json(client, url):
    resp = client.get('/api' + url)
    data = json.loads(resp.data.decode(encoding='utf-8'))
    return data


def test_api_basic():
    with app.test_client() as c:
        data = get_json(c, '/non-exists')
        assert data['code'] == Error.NO_SUCH_API.value[0]


def test_json_api_decorator():
    @json_api
    def return_none():
        return None

    @json_api
    def return_response():
        resp_ = make_response()
        resp_.status_code = 204
        return resp_

    @json_api
    def return_serializable():
        return 'abc'

    @json_api
    def return_iterable():
        a = [1, 2, 3]
        return filter(lambda x: x >= 2, a)

    @json_api
    def return_unknown():
        class A:
            pass

        return A()

    with raises(ApiException, error=Error.RESOURCE_NOT_EXISTS):
        return_none()

    with app.test_request_context('/api/posts'):
        assert return_response().status_code == 204
        resp = return_serializable()
        assert isinstance(resp, Response)
        assert resp.data == jsonify('abc').data
        resp = return_iterable()
        assert isinstance(resp, Response)
        assert resp.data == jsonify([2, 3]).data
        with raises(TypeError):
            return_unknown()


def test_site():
    with app.test_client() as c:
        data = get_json(c, '/site')
        assert data == site


def test_posts():
    with app.test_client() as c:
        data = get_json(c, '/posts')
        assert isinstance(data, list)
        assert len(data) == 3  # no drafts!
        assert 'My Post' in data[0]['title']

        data = get_json(c, '/posts/2017/')
        assert len(data) == 3
        data = get_json(c, '/posts?start=1&count=1')
        assert len(data) == 1
        data = get_json(c, '/posts?created=2016-03-02,2016-03-03&updated=')
        assert data['code'] == Error.INVALID_ARGUMENTS.value[0]
        data = get_json(c, '/posts?created=2016-03-02,2017-03-09&updated=2016-03-02,2017-03-09')
        assert len(data) == 2

        data = get_json(c, '/posts/2017/03/09/my-post')
        assert isinstance(data, dict)
        assert data['categories'] == ['Default']

        data = get_json(c, '/posts/2017/03/09/my-post/?fields=title,content,created,updated')
        assert 'categories' not in data

        data = get_json(c, '/posts/2017/03/09/non-exists')
        assert data['code'] == Error.RESOURCE_NOT_EXISTS.value[0]


def test_tags_categories():
    with app.test_client() as c:
        data = get_json(c, '/tags')
        assert {'name': 'Hello World', 'published': 1} in data

        data = get_json(c, '/categories')
        assert {'name': 'Default', 'published': 1} in data


def test_pages():
    with app.test_client() as c:
        data = get_json(c, '/pages/non-exists')
        assert data['code'] == Error.RESOURCE_NOT_EXISTS.value[0]

        data = get_json(c, '/pages/../../../../etc/passwd')
        assert data['code'] == Error.NOT_ALLOWED.value[0]

        resp = c.get('/api/pages/test-page.txt')
        assert resp.status_code == 200
        assert resp.content_type.startswith('text/plain')

        data = get_json(c, '/pages/my-page/')
        assert 'Lorem ipsum dolor sit amet.' in data['content']

        data = get_json(c, '/pages/test-page-draft')
        assert data['code'] == Error.RESOURCE_NOT_EXISTS.value[0]


def test_widgets():
    with app.test_client() as c:
        data = get_json(c, '/widgets')
        assert len(data) == 2

        data = get_json(c, '/widgets?position=header')
        assert data['code'] == Error.RESOURCE_NOT_EXISTS.value[0]

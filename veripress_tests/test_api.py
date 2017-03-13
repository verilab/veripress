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
        resp = make_response()
        resp.status_code = 204
        return resp

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
        assert len(data) == 4
        assert data[-1]['title'] == 'Hello, world!'

        data = get_json(c, '/posts/2017/')
        assert len(data) == 3
        data = get_json(c, '/posts?start=1&count=2')
        assert len(data) == 2
        data = get_json(c, '/posts?created=2016-03-02,2016-03-03&updated=')
        assert data['code'] == Error.INVALID_ARGUMENTS.value[0]
        data = get_json(c, '/posts?created=2016-03-02,2016-03-03&updated=2016-03-02,2016-03-03')
        assert len(data) == 1
        assert data[0]['title'] == 'Hello, world!'

        data = get_json(c, '/posts/2017/03/09/my-post')
        assert isinstance(data, dict)
        assert data['categories'] == ['Default']

        data = get_json(c, '/posts/2017/03/09/my-post/?fields=title,content,created,updated')
        assert 'categories' not in data

        data = get_json(c, '/posts/2017/03/09/non-exists')
        assert data['code'] == Error.RESOURCE_NOT_EXISTS.value[0]

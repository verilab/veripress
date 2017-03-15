import os

from pytest import raises
from werkzeug.exceptions import NotFound

from veripress import app, site, cache, create_app, CustomFlask


def test_create_app():
    an_app = create_app('config2.py')
    assert isinstance(an_app, CustomFlask)
    assert an_app.config['STORAGE_TYPE'] == 'fake_type'
    assert an_app.template_folder == os.path.join(
        os.environ.get('VERIPRESS_INSTANCE_PATH'), 'themes', 'fenki', 'templates'
    )
    assert hasattr(an_app, 'theme_static_folder')
    assert getattr(an_app, 'theme_static_folder') == os.path.join(
        os.environ.get('VERIPRESS_INSTANCE_PATH'), 'themes', 'fenki', 'static'
    )


def test_app():
    # app's config should be loaded from instance/config.py
    assert app.config['STORAGE_TYPE'] == 'file'
    assert app.config['THEME'] == 'test'

    with app.test_request_context('/'):
        app.send_static_file('no-use.css')
        app.send_static_file('no-use-2.css')
        with raises(NotFound):
            app.send_static_file('non-exists.css')

    origin_mode = app.config['MODE']
    app.config['MODE'] = 'api-only'
    with app.test_request_context('/'):
        with raises(NotFound):
            app.send_static_file('no-use.css')
    app.config['MODE'] = origin_mode


def test_site():
    # site meta info should be loaded from instance/site.json
    assert site['title'] == 'My Blog'
    assert site['subtitle'] == 'Yet another VeriPress blog.'


def test_cache():
    assert cache.config['CACHE_TYPE'] == 'null'


def test_webhook():
    with app.test_client() as c:
        resp = c.post('/_webhook', data={'a': 'A'})
        assert resp.status_code == 204

        script_path = os.path.join(app.instance_path, 'webhook.py')
        with open(script_path, 'rb') as f:
            script = f.read()

        os.remove(script_path)

        resp = c.post('/_webhook', data={'a': 'A'})
        assert resp.status_code == 204  # it should always return 204 although there is no 'webhook.py'

        with open(script_path, 'wb') as f:
            f.write(script)

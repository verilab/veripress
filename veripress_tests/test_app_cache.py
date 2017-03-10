import os

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


def test_site():
    # site meta info should be loaded from instance/site.json
    assert site['title'] == 'My Blog'
    assert site['subtitle'] == 'Yet another VeriPress blog.'


def test_cache():
    assert cache.config['CACHE_TYPE'] == 'null'

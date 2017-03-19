import json
import os

from flask import Flask, send_from_directory, current_app, abort
from werkzeug.exceptions import NotFound


class CustomFlask(Flask):
    """
    Customize the original Flask class to fit the needs of this VeriPress project.
    """

    def send_static_file(self, filename):
        """
        Send static files from the static folder in the current selected theme prior to the global static folder.

        :param filename: static filename
        :return: response object
        """
        if self.config['MODE'] == 'api-only':
            abort(404)  # if 'api-only' mode is set, we should not send static files

        theme_static_folder = getattr(self, 'theme_static_folder', None)
        if theme_static_folder:
            try:
                return send_from_directory(theme_static_folder, filename)
            except NotFound:
                pass
        return super(CustomFlask, self).send_static_file(filename)


def create_app(config_filename, instance_path=None):
    """
    Factory function to create Flask application object.

    :param config_filename: absolute or relative (rel to the instance path) filename of the config file
    :param instance_path: the instance path to initialize or run a VeriPress app
    :return: a Flask app object
    """
    app_ = CustomFlask(__name__,
                       instance_path=instance_path or os.environ.get('VERIPRESS_INSTANCE_PATH') or os.getcwd(),
                       instance_relative_config=True)
    app_.config.update(dict(STORAGE_TYPE='file',
                            THEME='default',
                            CACHE_TYPE='simple',
                            MODE='view-only',
                            ENTRIES_PER_PAGE=5,
                            FEED_COUNT=10,
                            SHOW_TOC=True,
                            TOC_DEPTH=3,
                            TOC_LOWEST_LEVEL=3,
                            ALLOW_SEARCH_PAGES=True))
    app_.config.from_pyfile(config_filename, silent=True)

    theme_folder = os.path.join(app_.instance_path, 'themes', app_.config['THEME'])
    app_.template_folder = os.path.join(theme_folder, 'templates')  # use templates in the selected theme's folder
    app_.theme_static_folder = os.path.join(theme_folder, 'static')  # use static files in the selected theme's folder
    app_.static_folder = os.path.join(app_.instance_path, 'static')  # global static folder

    return app_


app = create_app('config.py')

site = {
    'title': 'Untitled',
    'subtitle': 'Yet another VeriPress blog.'
}
try:
    with app.open_instance_resource('site.json', mode='r') as site_file:
        # load site meta info to the site object
        site.update(json.load(site_file))
except FileNotFoundError:
    pass


@app.route('/_webhook', methods=['POST'], strict_slashes=False)
def webhook():
    """
    Run a custom python script when requested.
    User can pull git repositories, log something to a file, or do anything else in there.

    :return: always 204 NO CONTENT
    """
    try:
        with current_app.open_instance_resource('webhook.py', 'r') as script_file:
            exec(script_file.read())  # if there is the 'webhook.py' script, we execute it's content
    except FileNotFoundError:
        pass
    return '', 204


from flask_caching import Cache
cache = Cache(app, config=app.config)  # create the cache object with the app's config

if app.config['MODE'] in ('mixed', 'api-only'):
    import veripress.api
    app.register_blueprint(api.api_blueprint, url_prefix='/api')

if app.config['MODE'] in ('mixed', 'view-only'):
    import veripress.view
    app.register_blueprint(view.view_blueprint)

import veripress.model

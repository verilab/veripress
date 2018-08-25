from datetime import datetime

from flask import current_app, g
from werkzeug.local import LocalProxy

import veripress.model.storages
from veripress.model.models import Base
from veripress.helpers import ConfigurationError


def get_storage():
    """
    Get storage object of current app context,
    will create a new one if not exists.

    :return: a storage object
    :raise: ConfigurationError: storage type in config is not supported
    """
    storage_ = getattr(g, '_storage', None)
    if storage_ is None:
        storage_type = current_app.config['STORAGE_TYPE']
        if storage_type == 'file':
            storage_ = g._storage = storages.FileStorage()
        else:
            raise ConfigurationError(
                'Storage type "{}" is not supported.'.format(storage_type))
    return storage_


storage = LocalProxy(get_storage)

from veripress import app


@app.teardown_appcontext
def teardown_storage(e):
    """
    Automatically called when Flask tears down the app context.
    This will close the storage object created at the beginning of the current app context.
    """
    storage_ = getattr(g, '_storage', None)
    if storage_ is not None:
        storage_.close()


class CustomJSONEncoder(app.json_encoder):
    """
    Converts model objects to dicts, datetime to timestamp,
    so that they can be serialized correctly.
    """

    def default(self, obj):
        if isinstance(obj, Base):
            return obj.to_dict()
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(CustomJSONEncoder, self).default(obj)


# use the customized JSON encoder when jsonify is called
app.json_encoder = CustomJSONEncoder

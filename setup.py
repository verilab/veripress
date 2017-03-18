"""
VeriPress
-----
VeriPress is a blog engine designed for hackers, based on Flask web framework.

````````````
Save in a hello.py:
.. code:: python
    from flask import Flask
    app = Flask(__name__)
    @app.route("/")
    def hello():
        return "Hello World!"
    if __name__ == "__main__":
        app.run()
And Easy to Setup
`````````````````
And run it:
.. code:: bash
    $ pip install Flask
    $ python hello.py
     * Running on http://localhost:5000/
 Ready for production? `Read this first <http://flask.pocoo.org/docs/deploying/>`.
Links
`````
* `website <http://flask.pocoo.org/>`_
* `documentation <http://flask.pocoo.org/docs/>`_
* `development version
  <https://github.com/pallets/flask/zipball/master#egg=Flask-dev>`_
"""

from distutils.core import setup

setup(
    name='VeriPress',
    version='1.0.0',
    packages=['veripress', 'veripress.api', 'veripress.model', 'veripress.view', 'veripress_cli'],
    url='https://github.com/veripress/veripress',
    license='The MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    install_requires=[
        'flask', 'flask-caching', 'pyyaml', 'mistune', 'pygments', 'feedgen'
    ],
    include_package_data=True,
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    )
)

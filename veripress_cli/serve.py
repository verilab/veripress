import click

from veripress_cli import cli


@cli.command('serve', short_help='Serve/Run the application.',
             help='This command will start an HTTP server '
                  'to serve the application.')
@click.option('--host', '-h', default='127.0.0.1',
              help='Host to serve the app.')
@click.option('--port', '-p', default=8080, help='Port to serve the app.')
def serve_command(host, port):
    click.echo('Starting HTTP server...')
    click.echo('HTTP server started. '
               'Running on http://{}:{}/'.format(host, port))

    from veripress import app
    try:
        from gevent.wsgi import WSGIServer
        server = WSGIServer((host, port), app)
        server.serve_forever()
    except ImportError:
        app.run(host=host, port=port)


@cli.command('preview', short_help='Preview the application.',
             help='This command will start an HTTP server '
                  'to preview the application. '
                  'You should never use this command to '
                  'run the app in production environment.')
@click.option('--host', '-h', default='127.0.0.1',
              help='Host to preview the app.')
@click.option('--port', '-p', default=8080, help='Port to preview the app.')
@click.option('--debug', is_flag=True, default=False,
              help='Preview in debug mode.')
def preview_command(host, port, debug):
    from veripress import app
    app.debug = debug
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['CACHE_TYPE'] = 'null'
    app.run(host=host, port=port, debug=debug)

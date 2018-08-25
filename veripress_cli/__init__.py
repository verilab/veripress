import click


@click.group(name='veripress',
             short_help='A blog engine for hackers.',
             help='This is a blog engine for hackers. '
                  'You can use this to serve a blog, '
                  'a wiki or anything else you like.')
@click.version_option(version='1.0.6')
def cli():
    pass


def main():
    cli.main()


import veripress_cli.init
import veripress_cli.serve
import veripress_cli.theme
import veripress_cli.generate
import veripress_cli.deploy

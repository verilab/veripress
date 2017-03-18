import click

cli = click.Group(help='This is a blog engine for hackers. '
                       'You can use this to serve a blog, a wiki or anything else you like.')


def main():
    cli.main()


import veripress_cli.init
import veripress_cli.serve
import veripress_cli.theme

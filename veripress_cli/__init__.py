import click

cli = click.Group()


def main():
    cli.main()


import veripress_cli.init
import veripress_cli.serve

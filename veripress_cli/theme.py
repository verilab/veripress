import os
import re
import shutil

import click

from veripress_cli import cli


def get_themes_dir():
    from veripress import app
    return os.path.join(app.instance_path, 'themes')


@cli.group(name='theme', short_help='Manage themes.',
           help='This set of sub-commands help you to manage themes.')
def theme_cli():
    pass


@theme_cli.command('list', short_help='List all themes installed.')
def list_command():
    themes = list(filter(
        lambda x: os.path.isdir(os.path.join(get_themes_dir(), x)),
        os.listdir(get_themes_dir())
    ))
    if not themes:
        click.echo('No theme is installed.')
        return
    click.echo('Themes installed:')
    click.echo('\n'.join(themes))


@theme_cli.command(
    'install', short_help='Install a theme from GitHub.',
    help='This command will install theme from GitHub for you. '
         'If you want to install a theme from the official '
         'veripress/themes repo, enter things like "default" '
         'to specify the theme. If you want to install a third-party theme, '
         'use "user/repo" format.\n\n'
         'e.g.\n\n'
         '  $ veripress theme install default\n\n'
         '  $ veripress theme install someone/the-theme '
         '--branch the-theme-branch\n\n'
         'If you want to customize the theme name installed, '
         'use "--name" parameter.'
)
@click.argument('theme', nargs=1)
@click.option('--branch', '-b', default='master',
              help='From which branch to clone the theme. '
                   'Only matters when a string like "user/repo" '
                   'is passed in as the theme name.')
@click.option('--name', '-n',
              help='Specify the theme name. '
                   'If this is not specified, a default one will be used.')
def install_command(theme, branch, name):
    if re.fullmatch('[_\-A-Z0-9a-z]+', theme):
        theme_name = name or theme
        theme_path = os.path.join(get_themes_dir(), theme_name)
        cmd = 'git clone --branch {} ' \
              'https://github.com/veripress/themes.git "{}"'.format(theme,
                                                                    theme_path)
    else:
        m = re.fullmatch('([_\-A-Z0-9a-z]+)/([_\-A-Z0-9a-z]+)', theme)
        if not m:
            raise click.BadArgumentUsage(
                'The theme should be like "default" '
                '(branch of veripress/themes) or "someone/the-theme" '
                '(third-party theme on GitHub)'
            )
        user = m.group(1)
        repo = m.group(2)
        theme_name = name or repo
        theme_path = os.path.join(get_themes_dir(), theme_name)
        cmd = 'git clone --branch {} ' \
              'https://github.com/{}/{}.git "{}"'.format(branch, user,
                                                         repo, theme_path)
    print(cmd)
    exit_code = os.system(cmd)
    if exit_code == 0:
        click.echo('\n"{}" theme has been '
                   'installed successfully.'.format(theme_name))
    else:
        click.echo('\nSomething went wrong. Do you forget to install git? '
                   'Or is there another theme with same name existing?')


@theme_cli.command('uninstall', short_help='Uninstall a theme.')
@click.argument('theme', nargs=1)
def uninstall_command(theme):
    theme_path = os.path.join(get_themes_dir(), theme)
    if os.path.isdir(theme_path):
        shutil.rmtree(theme_path)
        click.echo('"{}" theme has been '
                   'uninstalled successfully.'.format(theme))
    else:
        click.echo('There is no such theme.')


@theme_cli.command('update', short_help='Update a theme.')
@click.argument('theme', nargs=1)
def uninstall_command(theme):
    theme_path = os.path.join(get_themes_dir(), theme)
    if os.path.isdir(theme_path):
        cur_dir = os.getcwd()
        os.chdir(theme_path)
        exit_code = os.system('git pull')
        os.chdir(cur_dir)
        if exit_code == 0:
            click.echo('\n"{}" theme has been '
                       'updated successfully.'.format(theme))
        else:
            click.echo('\nSomething went wrong. '
                       'Do you forget to install git? '
                       'Or did you modify the theme by yourself?')
    else:
        click.echo('There is no such theme.')

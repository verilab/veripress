import os
import shutil
from datetime import datetime

import click

from veripress_cli import cli


@cli.command('init', short_help='Initialize a new instance directory.',
             help='This command will initialize the current working directory as a new VeriPress instance, '
                  'which means to create default configuration file, necessary subdirectories, etc.')
@click.option('--storage-mode', '-s', default='file', type=click.Choice(['file']),
              help='Storage mode (only "file" mode supported currently).')
def init_command(storage_mode):
    instance_path = os.getcwd()

    files = os.listdir(instance_path)
    if files:
        confirm = click.prompt('There are files in the instance path you entered. '
                               'Are you sure to remove them and continue? Y/N',
                               default='N', type=bool)
        if not confirm:
            return

    for file in files:
        path = os.path.join(instance_path, file)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    defaults_dir = os.path.join(os.path.dirname(__file__), 'defaults')

    with open(os.path.join(defaults_dir, 'config.py'), 'r', encoding='utf-8') as f_default_conf:
        with open(os.path.join(instance_path, 'config.py'), 'w', encoding='utf-8') as f_conf:
            f_conf.write(f_default_conf.read().format(storage_mode=storage_mode))

    shutil.copyfile(os.path.join(defaults_dir, 'site.json'),
                    os.path.join(instance_path, 'site.json'))
    shutil.copytree(os.path.join(defaults_dir, 'static'),
                    os.path.join(instance_path, 'static'))
    os.mkdir(os.path.join(instance_path, 'themes'))

    if storage_mode == 'file':
        init_file_storage(instance_path)

    click.echo('\nDefault files and configurations has been created!\n\n'
               'Now you should run "veripress theme install default" to install the default theme '
               'and then run "veripress preview" to preview the blog.\n\nEnjoy!')


def init_file_storage(instance_path):
    os.mkdir(os.path.join(instance_path, 'posts'))
    os.mkdir(os.path.join(instance_path, 'pages'))
    os.mkdir(os.path.join(instance_path, 'widgets'))

    now_dt = datetime.now()
    first_post_file_path = os.path.join(instance_path, 'posts', '{}-hello-world.md'.format(now_dt.strftime('%Y-%m-%d')))
    with open(first_post_file_path, 'w', encoding='utf-8') as f:
        f.write('---\ntitle: Hello, world!\ncreated: {}\n'
                'categories: Hello\ntags: [Hello, Greeting]\n---\n\n'.format(now_dt.strftime('%Y-%m-%d %H:%M:%S')))
        f.write('This is my first VeriPress post!\n')

    os.mkdir(os.path.join(instance_path, 'pages', 'first-page'))
    first_page_file_path = os.path.join(instance_path, 'pages', 'first-page', 'index.md')
    with open(first_page_file_path, 'w', encoding='utf-8') as f:
        f.write('---\ntitle: My First Page\ncreated: {}\n---\n\n'.format(now_dt.strftime('%Y-%m-%d %H:%M:%S')))
        f.write('This is my first custom page!\n')

    first_widget_file_path = os.path.join(instance_path, 'widgets', 'welcome.md')
    with open(first_widget_file_path, 'w', encoding='utf-8') as f:
        f.write('---\nposition: sidebar\norder: 0\n---\n\n')
        f.write('#### Welcome!\n\nHi! Welcome to my blog.\n')

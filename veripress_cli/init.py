import os
import shutil

import click

from veripress_cli import cli


@cli.command('init', short_help='Initialize a new instance directory.',
             help='This command will initialize the current working directory as a new VeriPress instance, '
                  'which means to create default configuration file, necessary subdirectories, etc.')
@click.option('--storage-mode', '-s', default='file', type=click.Choice(['file']),
              help='Storage mode (only "file" mode supported currently).')
@click.option('--instance-path', '-i', default=os.getcwd(), prompt='Which directory to initialize?',
              help='Where to place the new VeriPress instance.')
def init_command(storage_mode, instance_path):
    package_dir = os.path.dirname(__file__)
    if not os.path.isabs(instance_path):
        instance_path = os.path.abspath(instance_path)
    with open(os.path.join(package_dir, 'defaults', 'config.default.py'), 'r', encoding='utf-8') as f_default_conf:
        with open(os.path.join(instance_path, 'config.py'), 'w', encoding='utf-8') as f_conf:
            f_conf.write(f_default_conf.read().format(storage_mode=storage_mode))
    shutil.copyfile(os.path.join(package_dir, 'defaults', 'site.default.json'),
                    os.path.join(instance_path, 'site.json'))

    if storage_mode == 'file':
        init_file_storage(instance_path)


def init_file_storage(instance_path):
    pass

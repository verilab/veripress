import os
import re
from datetime import datetime

import click

from veripress_cli import cli
from veripress_cli.helpers import makedirs


def validate_repo_name(ctx, param, value):
    m = re.fullmatch('([_\-A-Z0-9a-z]+)/([_\-A-Z0-9a-z]+)', value)
    if not m:
        raise click.BadParameter('The repo name is invalid.')
    return m.groups()


@cli.command('setup-github-pages', short_help='Setup GitHub Pages.',
             help='This command will setup the deploy folder as a GitHub Pages repo.')
@click.option('--repo', '-r', prompt='Please enter your GitHub repo name, e.g. "someone/the-repo"',
              help='The GitHub repo name you want to deploy to.', callback=validate_repo_name)
@click.option('--name', '-n', prompt='Please enter your name (for git config)',
              help='Your name set in git config.')
@click.option('--email', '-e', prompt='Please enter your email (for git config)',
              help='Your email set in git config')
def setup_command(repo, name, email):
    user, repo = repo

    from veripress_cli.generate import get_deploy_dir
    deploy_dir = get_deploy_dir()
    makedirs(deploy_dir, mode=0o755, exist_ok=True)

    os.system('git -C {} init'.format(deploy_dir))
    os.system('git -C {} config user.email "{}"'.format(deploy_dir, email))
    os.system('git -C {} config user.name "{}"'.format(deploy_dir, name))
    os.system('git -C {} remote add origin git@github.com:{}/{}.git'.format(deploy_dir, user, repo))


@cli.command('deploy', short_help='Deploy GitHub Pages.',
             help='This command will deploy the static pages to GitHub Pages.')
def deploy_command():
    from veripress_cli.generate import get_deploy_dir
    deploy_dir = get_deploy_dir()
    makedirs(deploy_dir, mode=0o755, exist_ok=True)

    os.system('git -C {} add .'.format(deploy_dir))
    if os.system('git -C {} diff --quiet --exit-code'.format(deploy_dir)) == 0 \
            and os.system('git -C {} diff --quiet --cached --exit-code'.format(deploy_dir)) == 0:
        click.echo('There are no changes to be deployed.')
        return

    dt = datetime.now()
    os.system('git -C {} commit -m "Updated on {} at {}"'.format(deploy_dir,
                                                                 dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')))
    os.system('git -C {} push origin master'.format(deploy_dir))

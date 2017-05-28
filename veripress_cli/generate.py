import os
import math
import shutil

import click

from veripress_cli import cli
from veripress_cli.helpers import copy_folder_content, remove_folder_content, makedirs


def get_deploy_dir():
    from veripress import app
    return os.path.join(app.instance_path, '_deploy')


@cli.command('generate', short_help='Generate static pages.',
             help='This command will generate all HTML pages of the chosen instance.')
@click.option('--app-root', default='/',
              prompt='Please enter the application root (used as prefix of generated url)',
              help='The application root of your VeriPress instance. '
                   'For example, if you want to access the site through "http://example.com/blog/", '
                   'then "/blog/" should be passed in as the app root.')
def generate_command(app_root):
    deploy_dir = get_deploy_dir()
    if not os.path.isdir(deploy_dir):
        os.mkdir(deploy_dir)
    else:
        # remove all existing non-hidden files and dirs
        remove_folder_content(deploy_dir, ignore_hidden_file=True)

    from veripress import app

    app.config['APPLICATION_ROOT'] = app_root

    # mark as 'GENERATING_STATIC_PAGES' status, so that templates can react properly, e.g. remove search bar
    app.config['GENERATING_STATIC_PAGES'] = True

    do_generate()
    click.echo('\nOK! Now you can find all static pages in the "_deploy" folder.')


@cli.command('clean', short_help='Clean all generated static pages.',
             help='This command will clean all generated HTML pages of the chosen instance.')
def clean_command():
    deploy_dir = get_deploy_dir()
    if os.path.isdir(deploy_dir):
        remove_folder_content(get_deploy_dir(), ignore_hidden_file=True)
    click.echo('All generated static pages have been cleaned.')


def do_generate():
    from veripress import app
    from veripress.model import storage

    deploy_dir = get_deploy_dir()

    # copy global static folder
    dst_static_folder = os.path.join(deploy_dir, 'static')
    if os.path.isdir(app.static_folder):
        shutil.copytree(app.static_folder, dst_static_folder)

    # copy theme static files
    makedirs(dst_static_folder, mode=0o755, exist_ok=True)
    copy_folder_content(app.theme_static_folder, dst_static_folder)

    # collect all possible urls (except custom pages)
    all_urls = {'/', '/feed.xml', '/atom.xml', '/archive/'}
    with app.app_context():
        posts = list(storage.get_posts(include_draft=False))

        index_page_count = int(math.ceil(len(posts) / app.config['ENTRIES_PER_PAGE']))
        for i in range(2, index_page_count + 1):  # ignore '/page/1/', this will be generated separately later
            all_urls.add('/page/{}/'.format(i))

        for post in posts:
            all_urls.add(post.unique_key)
            all_urls.add('/archive/{}/'.format(post.created.strftime('%Y')))
            all_urls.add('/archive/{}/{}/'.format(post.created.strftime('%Y'), post.created.strftime('%m')))

        tags = storage.get_tags()
        for tag_item in tags:
            all_urls.add('/tag/{}/'.format(tag_item[0]))

        categories = storage.get_categories()
        for category_item in categories:
            all_urls.add('/category/{}/'.format(category_item[0]))

    with app.test_client() as client:
        # generate all possible urls
        for url in all_urls:
            resp = client.get(url)
            file_path = os.path.join(get_deploy_dir(), url.lstrip('/').replace('/', os.path.sep))
            if url.endswith('/'):
                file_path += 'index.html'

            makedirs(os.path.dirname(file_path), mode=0o755, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(resp.data)

        # generate 404 page
        resp = client.get('/post/this-is-a-page-that-never-gonna-exist'
                          '-because-it-is-a-post-with-wrong-url-format/')
        with open(os.path.join(deploy_dir, '404.html'), 'wb') as f:
            f.write(resp.data)

    if app.config['STORAGE_TYPE'] == 'file':
        generate_pages_by_file()


def generate_pages_by_file():
    """Generates custom pages of 'file' storage type."""
    from veripress import app
    from veripress.model import storage
    from veripress.model.parsers import get_standard_format_name
    from veripress.helpers import traverse_directory

    deploy_dir = get_deploy_dir()

    def copy_file(src, dst):
        makedirs(os.path.dirname(dst), mode=0o755, exist_ok=True)
        shutil.copyfile(src, dst)

    with app.app_context(), app.test_client() as client:
        root_path = os.path.join(app.instance_path, 'pages')
        for path in traverse_directory(root_path):
            rel_path = os.path.relpath(path, root_path)  # e.g. 'a/b/c/index.md'
            filename, ext = os.path.splitext(rel_path)  # e.g. ('a/b/c/index', '.md')
            if get_standard_format_name(ext[1:]) is not None:
                # is source of custom page
                rel_url = filename.replace(os.path.sep, '/') + '.html'  # e.g. 'a/b/c/index.html'
                page = storage.get_page(rel_url, include_draft=False)
                if page is not None:
                    # it's not a draft, so generate the html page
                    makedirs(os.path.join(deploy_dir, os.path.dirname(rel_path)), mode=0o755, exist_ok=True)
                    with open(os.path.join(deploy_dir, filename + '.html'), 'wb') as f:
                        f.write(client.get('/' + rel_url).data)
                if app.config['PAGE_SOURCE_ACCESSIBLE']:
                    copy_file(path, os.path.join(deploy_dir, rel_path))
            else:
                # is other direct files
                copy_file(path, os.path.join(deploy_dir, rel_path))

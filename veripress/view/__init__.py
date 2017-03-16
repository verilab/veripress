import os
import functools
from itertools import chain

from flask import Blueprint, request, render_template

from veripress import site
from veripress.model import storage
from veripress.model.parsers import get_parser
from veripress.helpers import url_rule, to_list

view_blueprint = Blueprint('view', __name__)


@view_blueprint.context_processor
def inject_context():
    """
    Inject some common objects into the context of templates.
    """
    return dict(site=site, storage=storage)


@view_blueprint.app_template_filter('content')
def parse_content_of_models(obj):
    """
    Parse the whole 'raw_content' attribute of a Post or Page or Widget object (in template files).

    :param obj: a Post or Page or Widget object
    :return: parsed whole content
    """
    return get_parser(obj.format).parse_whole(obj.raw_content)


def custom_render_template(template_name_or_list, **context):
    """
    Try to render templates in the custom folder first, if no custom templates, try the theme's default ones.
    """
    return render_template(
        functools.reduce(lambda x, y: x + [os.path.join('custom', y), y], to_list(template_name_or_list), []),
        **context
    )


def templated(template=None, *templates):
    """
    Decorate a view function with one or more default template name.
    This will try templates in the custom folder first, the theme's original ones second.

    :param template: template name or template name list
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            template_ = template
            if template_ is None:
                template_ = request.endpoint.replace('.', '/') + '.html'
            context = func(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context
            return custom_render_template(list(chain(to_list(template_), templates)), **context)

        return wrapper

    return decorator


@view_blueprint.errorhandler(404)
@templated('404.html')
def page_not_found(e):
    pass


from veripress.view import views

rule = functools.partial(url_rule, view_blueprint, methods=['GET'])

rule(['/feed.xml', '/feed/', '/atom.xml'], view_func=views.feed, strict_slashes=True)

rule(['/', '/page/<int:page_num>/'], view_func=views.index, strict_slashes=True)
rule('/post/<int:year>/<int:month>/<int:day>/<string:post_name>', view_func=views.post, strict_slashes=False)
rule('/category/<string:category_name>/', view_func=views.category, strict_slashes=True)
rule('/tag/<string:tag_name>/', view_func=views.tag, strict_slashes=True)
rule(['/archive/',
      '/archive/<int:year>/',
      '/archive/<int:year>/<int:month>/'], view_func=views.archive, strict_slashes=True)
rule('/search', view_func=views.search, strict_slashes=False)
rule('/<path:rel_url>', view_func=views.page, strict_slashes=True)

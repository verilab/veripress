from datetime import datetime

from veripress import site
from veripress.helpers import to_list, to_datetime


class Base(object):
    """
    Base model class, contains basic/general information of a post/page/widget.
    """

    def __init__(self):
        self.meta = {}
        self.raw_content = None
        self._format = None

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        if value is not None:
            self._format = value.lower()

    @property
    def is_draft(self):
        return self.meta.get('is_draft', False)

    def to_dict(self):
        """
        Convert attributes and properties to a dict (so that it can be serialized).

        :return: a dict
        """
        return {k: getattr(self, k) for k in filter(lambda k: not k.startswith('_') and k != 'to_dict', dir(self))}


class AuthorMixIn(object):
    """
    Mix in author's name and email.
    """

    @property
    def author(self):
        return getattr(self, 'meta', {}).get('author', site.get('author'))

    @property
    def email(self):
        return getattr(self, 'meta', {}).get('email', site.get('email'))


class DateMixIn(object):
    """
    Mix in created data and updated date.
    """

    @property
    def created(self):
        return to_datetime(getattr(self, 'meta', {}).get('created'))

    @property
    def updated(self):
        return to_datetime(getattr(self, 'meta', {}).get('updated', self.created))


class TagCategoryMixIn(object):
    """
    Mix in tags and categories.
    """

    @property
    def tags(self):
        return to_list(getattr(self, 'meta', {}).get('tags', []))

    @property
    def categories(self):
        return to_list(getattr(self, 'meta', {}).get('categories', []))


class Page(Base, AuthorMixIn, DateMixIn):
    """
    Model class of publish type 'custom page' or 'page', with default layout 'page'.
    """
    _default_layout = 'page'

    def __init__(self):
        super().__init__()
        self.unique_key = None
        self.rel_url = None

    @property
    def layout(self):
        return self.meta.get('layout', self._default_layout)

    @property
    def title(self):
        result = self.meta.get('title')
        if result is None and self.rel_url:
            sp = self.rel_url.split('/')
            pos = len(sp) - 1
            while pos > 0 and (sp[pos] == 'index.html' or not sp[pos]):
                pos -= 1

            path_seg = sp[pos][:-len('.html')] if sp[pos].endswith('.html') else sp[pos]
            result = ' '.join(word[0].upper() + word[1:] for word in filter(lambda x: x, path_seg.split('-')))
        return result


class Post(Page, TagCategoryMixIn):
    """
    Model class of publish type 'post', with default layout 'post'.
    """
    _default_layout = 'post'

    @property
    def created(self):
        result = super(Post, self).created
        if result is None:
            d, _, _ = self.rel_url.rsplit('/', 2)
            result = datetime.strptime(d, '%Y/%m/%d')
        return result

    @property
    def title(self):
        result = self.meta.get('title')
        if result is None:
            _, post_name, _ = self.rel_url.rsplit('/', 2)
            result = ' '.join(word[0].upper() + word[1:] for word in filter(lambda x: x, post_name.split('-')))
        return result


class Widget(Base):
    """
    Model class of publish type 'widget'.
    """

    @property
    def position(self):
        return self.meta.get('position')

    @property
    def order(self):
        return self.meta.get('order')

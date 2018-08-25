import re
from html.parser import HTMLParser


class _HtmlHeaderNode(object):
    """Represents a header element when parsing the HTML string."""

    def __init__(self, level):
        """Initialize attributes."""
        # header level of the element, e.g. 1 for <h1>, 2 for <h2>, etc
        self.level = level
        # anchor id (in-page link),
        # used in 'id' and 'href' attribute of 'a' tag
        self.id = ''
        # pure text content of header tag, e.g. 'Title' for '<h1>Title</h1>'
        self.text = ''
        # inner HTML
        self.inner_html = ''
        # point to the direct father node
        self.father = None
        # elements with lower levels that directly follows the current elem
        self.children = []

    def to_dict(self):
        """Convert self to a dict object for serialization."""
        return {
            'level': self.level,
            'id': self.id,
            'text': self.text,
            'inner_html': self.inner_html,
            'children': [child.to_dict() for child in self.children]
        }


class HtmlTocParser(HTMLParser):
    """Parse table of content from a given HTML string."""

    # regular expression for replacing all punctuations in the header with '-'
    _punctuations_exp = re.compile(
        r'[\s\u0020-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007e'
        r'\u00a0-\u00bf\u2000-\u206f\u2e00-\u2e7f\u3000-\u303f'
        r'\uff01-\uff0f\uff1a-\uff20\uff3b-\uff40\uff5b-\uff65'
        r'\uffe0-\uffe6\uffe8-\uffec\ufe10-\ufe1f]+'
    )

    def __init__(self):
        """Initialize attributes."""
        super().__init__(convert_charrefs=False)
        # root node with no data of itself, only 'children' matters
        self._root = _HtmlHeaderNode(level=0)
        # most recently handled header node
        self._curr_node = self._root
        self._in_header = False
        # record header ids to avoid collisions
        self._header_id_count = {}
        # full HTML string parsed
        self._html = ''
        # temporary HTML start tag of this current header node
        self._temp_start_tag = ''

    def toc(self, depth=6, lowest_level=6):
        """
        Get table of content of currently fed HTML string.

        :param depth: the depth of TOC
        :param lowest_level: the allowed lowest level of header tag
        :return: a list representing the TOC
        """
        depth = min(max(depth, 0), 6)
        depth = 6 if depth == 0 else depth
        lowest_level = min(max(lowest_level, 1), 6)
        toc = self._root.to_dict()['children']

        def traverse(curr_toc, dep, lowest_lvl, curr_depth=1):
            if curr_depth > dep:
                # clear all items of this depth and exit the recursion
                curr_toc.clear()
                return

            items_to_remove = []
            for item in curr_toc:
                if item['level'] > lowest_lvl:
                    # record item with low header level, for removing it later
                    items_to_remove.append(item)
                else:
                    traverse(item['children'], dep, lowest_lvl, curr_depth + 1)
            [curr_toc.remove(item) for item in items_to_remove]

        traverse(toc, depth, lowest_level)
        return toc

    def toc_html(self, depth=6, lowest_level=6):
        """
        Get TOC of currently fed HTML string in form of HTML string.

        :param depth: the depth of TOC
        :param lowest_level: the allowed lowest level of header tag
        :return: an HTML string
        """
        toc = self.toc(depth=depth, lowest_level=lowest_level)
        if not toc:
            return ''

        def map_toc_list(toc_list):
            result = ''
            if toc_list:
                result += '<ul>\n'
                result += ''.join(
                    map(lambda x: '<li>'
                                  '<a href="#{}">{}</a>{}'
                                  '</li>\n'.format(
                        x['id'], x['inner_html'],
                        map_toc_list(x['children'])),
                        toc_list)
                )
                result += '</ul>'
            return result

        return map_toc_list(toc)

    @property
    def html(self):
        """
        The parsed HTML string with additional tags marking the header anchors.

        Example:
            `<h1>Title</h1>`

            becomes:

            `<h1><a id="Title" class="anchor"></a>Title</h1>`
        """
        return self._html

    @staticmethod
    def _get_level(tag):
        """
        Match the header level in the given tag name,
        or None if it's not a header tag.
        """
        m = re.match(r'^h([123456])$', tag, flags=re.IGNORECASE)
        if not m:
            return None
        return int(m.group(1))

    def handle_starttag(self, tag, attrs):
        curr_tag = '<{}{}{}>'.format(
            tag, ' ' if attrs else '',
            ' '.join(['{}="{}"'.format(*attr) for attr in attrs]))

        if self._in_header:
            self._curr_node.inner_html += curr_tag
            return

        level = self._get_level(tag)
        if level is not None:
            self._in_header = True
            new_node = _HtmlHeaderNode(level=level)
            while new_node.level <= self._curr_node.level:
                # the new node is a higher level header, e.g. new: h2, curr: h4
                # so we return back until the current is higher
                self._curr_node = self._curr_node.father
            # assign the new node as a child of the current node
            new_node.father = self._curr_node
            self._curr_node.children.append(new_node)
            self._curr_node = new_node
            self._temp_start_tag = curr_tag
            return

        self._html += curr_tag

    def handle_startendtag(self, tag, attrs):
        curr_tag = '<{}{}{} />'.format(
            tag, ' ' if attrs else '',
            ' '.join(['{}="{}"'.format(*attr) for attr in attrs]))

        if self._in_header:
            self._curr_node.inner_html += curr_tag
            return

    def handle_endtag(self, tag):
        curr_tag = '</{}>'.format(tag)

        if self._get_level(tag) is not None:
            header_id = self._punctuations_exp.sub(
                '-', self._curr_node.text).strip('-')
            count = self._header_id_count.setdefault(header_id, 0)
            self._header_id_count[header_id] += 1
            if count > 0:
                header_id += '_%d' % count

            self._curr_node.id = header_id
            # start tag of the current header node
            self._html += self._temp_start_tag
            # anchor
            self._html += \
                '<a id="{0}" href="#{0}" class="anchor"></a>'.format(header_id)
            # header content and end tag
            self._html += self._curr_node.inner_html + curr_tag
            self._temp_start_tag = ''
            self._in_header = False
            return
        elif self._in_header:
            self._curr_node.inner_html += curr_tag
            return

        self._html += curr_tag

    def handle_data(self, data):
        if self._in_header:
            self._curr_node.text += data
            self._curr_node.inner_html += data
            return

        self._html += data

    def handle_comment(self, data):
        self.handle_data('<!--{}-->'.format(data))

    def handle_entityref(self, name):
        self.handle_data('&{};'.format(name))

    def handle_charref(self, name):
        self.handle_data('&#{};'.format(name))

    def error(self, message):
        pass  # pragma: no cover

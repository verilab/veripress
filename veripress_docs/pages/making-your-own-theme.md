---
title: 制作主题
author: Richard Chien
created: 2017-03-21
updated: 2017-03-21
---

VeriPress 原生支持主题，如果你对官方主题或其它第三方主题感到不满意，同时也有一定的编程基本知识，你就可以自行制作自己的主题，也欢迎你把自己制作的主题发布到网上和其他人一起分享。

## 主题的组成部分

主题主要包括静态文件和模板文件，分别在 `static` 子目录和 `templates` 子目录。

`static` 中的文件，可以直接通过 `/static/:path` 来访问，例如 `/static/style.css` 可以访问到当前正在使用的主题的 `static/style.css` 文件，而如果当前主题的 `static` 目录中并没有 `style.css` 文件，则会去 VeriPress 实例的全局 `static` 目录中寻找。

`templates` 中的模板文件，会在收到请求后按照所请求的内容渲染成最终的 HTML 页面，必须存在的模板有 `index.html`、`archive.html`，这两个分别对应首页和归档页；而如果文章和自定义页面使用了默认的布局（分别 `post` 和 `page`），则还必须有 `post.html`、`page.html`；此外，标签、分类、搜索三个页面在没有单独模板的情况下都默认使用 `archive.html`，如果你需要单独定义这三类页面，使用 `tag.html`、`category.html`、`search.html` 来命名。除了上面各个对应实际页面的模板，还有一个 `404.html` 用于在找不到页面的情况下渲染。

VeriPress 在寻找模板文件时，首先会查找主题的 `templates/custom` 目录，如果在里面找到了相应的模板，将使用它（用户自定义的模板），如果没找到，将使用 `templates` 中的模板。

## 模板引擎

VeriPress 使用 Jinja2 模板引擎，下面简单介绍它的语法。

`{{ ... }}` 用来表示表达式，模板文件在渲染时会传入一些值（后面解释），这些值可以通过形如 `{{ some_object.some_attribute }}` 的表达式来取出，表达式的计算结果将会转成 HTML 显示在相应的位置。

`{% ... %}` 用来表示语句，比如判断语句、循环语句等，通过多个这样的块将语句主体包在中间，例如一个判断结构：

```html
{% if True %}
  <p>{{ some_variable }}</p>
{% endif %}
```

限于篇幅这里也不重复太多 Jinja2 的文档了，具体的语法请参考 [Template Designer Documentation](http://jinja.pocoo.org/docs/2.9/templates/)。

下面将解释渲染模板时「传入的值」。

## 渲染模板的 Context

渲染模板时有个概念叫 context，也就是在模板渲染时可以接触到的 Python 环境中的函数、对象等。由于基于 Flask，因此所有 Flask 的 context，都可以使用，例如 `request`、`config`、`session`、`url_for()` 等，通过这些，便可以访问到当前的请求 URL、参数、配置文件等，可以参考 [Standard Context](http://flask.pocoo.org/docs/0.12/templating/#standard-context)。

除了 Flask 提供的这些，对于不同的模板文件，VeriPress 还提供了该模板可能会需要用到的对象，如下表：

| 模板              | 额外的 Context 对象                          | 说明                                       |
| --------------- | --------------------------------------- | ---------------------------------------- |
| `index.html`    | `entries`、`next_url`、`prev_url`         | 分别是当前分页上的文章列表、下一页的 URL、上一页的 URL          |
| `post.html`     | `entry`                                 | 当前访问的文章                                  |
| `page.html`     | `entry`                                 | 当前访问的自定义页面                               |
| `archive.html`  | `entries`、`archive_type`、`archive_name` | 分别是当前归档的文章列表、归档类型、归档名称，其中 `/archive/` 页面的归档类型为 `Archive`，名称为 `All` 或类似 `2017`、`2017.3`（分别对应 `/archive/2017/` 和 `/archive/2017/03/` 页面） |
| `tag.html`      | 同上                                      | 归档类型为 `Tag`，归档名称为标签名                     |
| `category.html` | 同上                                      | 归档类型为 `Category`，归档名称为分类名                |
| `search.html`   | 同上                                      | 归档类型为 `Search`，归档名称为搜索关键词加引号             |

以上的「文章」「自定义页面」的数据，基本上和 [API 模式](api-mode.html#api-posts-获取文章列表) 获取到的相似，不同之处在于此处每个对象都多了一个 `url` 字段，可以用来直接构造链接。

除了上述的每个模板不同的 context 对象，每个模板内都可以访问 `site` 和 `storage` 两个对象，前者即 `site.json` 中的内容，后者是当前使用的存储类型的数据访问封装对象，一般很少会直接用这个，只有在获取页面部件时有必要使用（因为不是所有页面都需要显示部件，何时显示由主题决定）。由于 `storage` 获取到的数据是最原始的文章、页面、部件的对象，这里不再花费篇幅列出它的方法和获取的对象中的属性了，请直接参考 [model/storages.py](https://github.com/veripress/veripress/blob/master/veripress/model/storages.py) 中的 `Storage` 类和 [model/models.py](https://github.com/veripress/veripress/blob/master/veripress/model/models.py) 中的类定义。

**鉴于获取页面部件需要使用 `storage` 对象，如果你没有精力或兴趣查看源码，可以直接参考默认主题的 [sidebar.html](https://github.com/veripress/themes/blob/default/templates/sidebar.html) 文件。**

在上面的 `sidebar.html` 中你会看到一个 `{{ widget|content|safe }}` 这样的表达式，其中 `widget` 是获取到的页面部件对象，后面两个 `content`、`safe` 是「过滤器」，前者是 VeriPress 提供的，用于把内容的抽象对象中的原始内容直接解析成 HTML 字符串，后者是 Jinja2 自带的，用于将 HTML 代码直接显示而不转义。

## 获取特定页面的 URL

在主题中你可能需要获取其它某个页面的 URL 来构造链接，可以使用 Flask 提供的 `url_for()` 函数。

对于全局或主题中的 `static` 目录的文件，使用 `url_for('static', filename='the-filename')` 来获取。

对于 view 模式的其它页面，例如你在导航栏需要提供一个归档页面的链接，使用类似 `url_for('.archive', year=2017)` 的调用。注意 `.archive` 以点号开头，或者也可以使用 `view.archive`。`url_for()` 的其它参数是用来指定 view 函数的参数的，要熟练使用的话，你可能需要对 Flask 的 URL route 规则有一定了解，然后参考 [view/\_\_init\_\_.py](https://github.com/veripress/veripress/blob/master/veripress/view/__init__.py) 文件最底部的 URL 规则。

## 调试主题

制作主题时可能会出现异常（Exception），如果直接显示「500 Internal Error」可能没什么帮助，这时可以使用 `veripress preview --debug` 来预览，`--debug` 选项将开启 Flask 的调试模式，在抛出异常时会将异常信息显示在页面上。

## 制作主题时遇到问题？

不得不承认这篇关于如何制作主题的文档写的非常简陋，如果你在自己制作过程中遇到不太明确的事情，在这里也找不到的话，首先可以参考官方主题，如果还有疑问（或者对官方主题的写法不太认同），请毫不吝啬地提交 [issue](https://github.com/veripress/veripress/issues/new)。

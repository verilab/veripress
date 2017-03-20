---
title: 配置文件
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

`config.py` 文件即 VeriPress 的配置文件，初始化实例之后会生成一份默认的配置，多数情况下，你可能需要秀改配置文件来符合个性化的需求，同时，配置文件可以被主题模板获取到，因此某些主题可能会对配置文件的某些项的不同配置表现出不同的行为。

下面给出 VeriPress 和默认主题所支持的配置项的说明（对于第三方主题特定的配置项要求，请参考它们的作者给出的使用方式）。

## STORAGE_TYPE

指定内容的存储方式。

VeriPress 在设计时允许了未来加入不同的存储方式（比如数据库存储），而不限于使用文件存储。不过目前只支持文件存储，所以此项应该填默认的 `file`。

## THEME

指定要使用的主题。

默认为 `default`，即使用 default 主题，如果你安装了其它主题，就可以修改这个配置来更换主题，比如你现在看到的文档使用了 clean-doc 主题，可以使用 `veripress theme install clean-doc` 安装。

## CACHE_TYPE

指定缓存类型。

默认的 `simple` 表示使用简单的内存缓存。VeriPress 的缓存使用了 Flask-Caching 扩展，支持如下类型：

| 配置值             | 说明                |
| --------------- | ----------------- |
| `null`          | 不使用缓存             |
| `simple`        | 简单内存缓存            |
| `memcached`     | Memcached 缓存      |
| `gaememcached`  | GAE memcached 缓存  |
| `saslmemcached` | SASL memcached 缓存 |
| `redis`         | Redis 缓存          |
| `filesystem`    | 文件系统缓存            |

对于除了 `null`、`simple` 之外的配置，还需要提供其它所需的配置项，例如使用 `redis` 则需要另外提供 `CACHE_REDIS_HOST`、`CACHE_REDIS_PORT` 等，请参考 Flask-Caching 的文档 [Configuring Flask-Caching](https://pythonhosted.org/Flask-Caching/#configuring-flask-caching)。

## MODE

指定运行模式。

VeriPress 支持三种运行模式：`view-only`、`api-only`、`mixed`。`view-only` 表示只能访问页面，无法通过 API 直接获取 JSON 数据；`api-only` 表示只能通过 API 获取 JSON 数据；`mixed`，顾名思义，前两者混合模式。

关于 API 模式的更多信息，请参考 [API 模式](api-mode.html)。

## ENTRIES_PER_PAGE

指定首页文章列表每页显示的文章数量。

默认情况下网站的首页是文章（post）列表，并通过 URL `/page/<page_num>/` 来分页，因此需要指定每页显示的文章数量。对于会显示内容预览的主题，这个值可以设置小一些，而不显示预览的主题，可以设置大一些。

## FEED_COUNT

指定 Atom 订阅中的文章数量。

例如设置为 10 则 Atom 订阅中只会生成最新的 10 篇文章。

## SHOW_TOC

指定是否显示 TOC（目录）。

实际上此配置项是控制 VeriPress 内部是否生成 TOC，如果设置成 `False` 则主题模板无法收到 TOC。相反，设置成 `True` 则主题模板可以收到一个 TOC 列表和 TOC HTML 字符串，但是否显示最终取决于主题。

## TOC_DEPTH 和 TOC_LOWEST_LEVEL

指定 TOC 的最大深度和最低标题级别。

这两个范围都是 1～6，两个含义有一定区别。首先给一个 HTML 的示例：

```html
<h6>Title 1</h6>
<h1>Title 2</h1>
  <h2>Title 3</h2>
    <h4>Title 4</h4>
    <h3>Title 5</h3>
<h1>Title 6</h1>
  <h5>Title 7</h5>
```

对于上面的示例，在不限最大深度和最低标题级别的情况下，生成的 TOC 应该和给出的缩进相同。可以发现 Title 1 也在生成的 TOC 中，如果想过滤掉这种级别比较低的标题，可以设置 `TOC_LOWEST_LEVEL` 为比较小的值，比如设置为 4，则 `h5`、`h6` 标签都不会算在内。同时可以发现这个 TOC 有三层，如果只需要显示两层，可以将 `TOC_DEPTH` 设置为 2。

## ALLOW_SEARCH_PAGES

指定是否允许搜索自定义页面的内容。

只在动态运行时有效（生成静态文件之后没法搜索）。设置为 `False` 则在搜索时不会搜索自定义页面的内容。另外，只支持搜索 VeriPress 中解析器所支持的格式中的文字，例如使用 Markdown 编写的自定义页面，相反地，直接的 HTML 文件或其它静态文件无法被搜索到。

## DUOSHUO_ENABLED、DUOSHUO_SHORT_NAME、DISQUS_ENABLED 和 DISQUS_SHORT_NAME

指定是否开启多说或 Disqus 评论框，以及它们的 shortname。

default 主题和 clean-doc 主题支持多说和 Disqus 评论框，例如设置：

```py
DUOSHUO_ENABLED = True
DUOSHUO_SHORT_NAME = 'your-shorname'
```

将会在文章和自定义页面底部显示多说评论框，Disqus 同理。

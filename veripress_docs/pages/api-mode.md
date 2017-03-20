---
title: API 模式
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

当运行模式 `MODE` 设置为 `api-only` 或 `mixed` 时，即开启了 API 模式，这种情况下，可以通过 `/api` 前缀来访问 API，由此将可以不受 VeriPress 页面划分逻辑的限制（只有首页的文章列表可以分页，标签、分类、归档、搜索页面默认不分页，这些限制是为了保持动态和静态运行的体验一致性），而直接在前端去获取数据并按想要的方式显示。

## 基础知识

### API 可以获取什么？

API 模式开放的这些 API，只能获取和页面上显示的同样的文章列表、自定义页面和页面部件等，也就是说，设置为草稿的内容将无法获取到。同时目前也无法获取自定义页面的列表（因为这一内容形式变化性比较强，暂时没有较好的办法提供 API），只能通过具体路径获取单个页面。

另外，在获取文章列表时，返回的结果只有预览部分，获取单个文章时，则返回全部正文内容。

### API 的请求方式

所有 API 均使用 GET 方式来请求，当 HTTP 响应码为 200 时表示请求成功，这意味着请求的资源存在，并成功获取，返回的 JSON 中将直接包含该资源的数据，在后面的 API 列表中分别给出。状态码 4xx 表示请求失败，具体的错误状态码根据情况而不同，此时返回的 JSON 数据有 `code` 和 `message` 两个字段，分别是错误码和错误信息，例如：

```json
{
  "code": 101, 
  "message": "No such API."
}
```

不同的 HTTP 状态码、错误码对应错误原因如下表：

| 错误码  | HTTP 状态码 | 错误原因        |
| ---- | -------- | ----------- |
| 100  | 400      | 未定义的错误      |
| 101  | 404      | API 不存在     |
| 102  | 404      | 资源不存在       |
| 103  | 400      | 请求参数不正确     |
| 104  | 403      | 请求的资源路径不被允许 |
| 105  | 400      | 请求的资源路径无法识别 |

## API 列表

### /api/posts 获取文章列表

可以接受的 URL 参数如下：

| 参数名                                      | 说明                                       |
| ---------------------------------------- | ---------------------------------------- |
| `title`、`layout`、`author`、`email`、`tags`、`categories` | 用于限定文章的元信息，可以多选，用英文逗号分隔                  |
| `created`、`updated`                      | 用于限定创建和更新日期，每个参数必须是用逗号分隔的两个值，格式如 `2017-03-20`，分别为开始日期和截止日期 |
| `start`                                  | 经过所有筛选之后，返回数据列表的第一个的下标                   |
| `count`                                  | 获取的文章数量                                  |
| `fields`                                 | 指定要获取的文章信息的字段名，可多选，用逗号分隔                 |

例如请求 `/api/posts?layout=post&tags=Hello,Greeting&created=2017-01-01,2017-03-20&start=10&count=10&fields=title,author,created,updated,preview` 将返回布局为 `post`、有 `Hello` 或 `Greeting` 标签、在 2017-01-01 到 2017-03-20 之间创建的所有文章的第 10 条到第 19 条的 `title`、`author`、`created`、`updated`、`preview` 字段。

除了 URL 参数之外，还可以通过路径来对返回结果进行筛选（注意这里的筛选会在通过 `start` 和 `count` 参数取子列表之前进行），形如 `/api/posts/<int:year>/<int:month>/<int:day>/<string:post_name>`，四个路径参数分别表示创建年份、月份、日期、文章名（不是标题，是显示在 URL 中的文章名），可以从后往前依次省略。一旦指定了最后一个文章名，返回结果将不再是 JSON 数组，而是单个文章的 JSON 对象。

响应数据如下（没有精确指定到文章名的情况）：

```json
[
  {
    "author": "My Name", 
    "categories": ["Mauris"], 
    "created": "2017-03-16 00:00:00", 
    "email": "someone@example.com", 
    "format": "txt", 
    "has_more_content": false, 
    "is_draft": false, 
    "layout": "post", 
    "meta": {
      "categories": ["Mauris"], 
      "tags": ["Blog"], 
      "title": "Lorem Ipsum"
    }, 
    "preview": "<pre class=\"txt\">abcd</pre>", 
    "rel_url": "2017/03/16/viverra/", 
    "tags": ["Blog"], 
    "title": "Lorem Ipsum", 
    "unique_key": "/post/2017/03/16/viverra/", 
    "updated": "2017-03-16 00:00:00"
  }, 
  {
    "author": "My Name", 
    "categories": ["Donec"], 
    "created": "2017-03-04 00:00:00", 
    "email": "someone@example.com", 
    "format": "markdown", 
    "has_more_content": true, 
    "is_draft": false, 
    "layout": "post", 
    "meta": {
      "categories": ["Donec"], 
      "tags": ["VeriPress"], 
      "title": "Some Title"
    }, 
    "preview": "The preview part of content.", 
    "rel_url": "2017/03/04/lacinia/", 
    "tags": ["VeriPress"], 
    "title": "\u5f3a\u5212\u9ad8\u9898\u7c7b\u5546", 
    "unique_key": "/post/2017/03/04/lacinia/", 
    "updated": "2017-03-04 00:00:00"
  }
]
```

其中每个文章对象的字段说明如下：

| 字段名                | 说明                                       |
| ------------------ | ---------------------------------------- |
| `format`           | 撰写文章所使用的格式                               |
| `is_draft`         | 是否草稿（API 所能获取到的全为 false）                 |
| `meta`             | 文章的原始元信息，保留了文件中的 YAML 头解析之后的最原始信息        |
| `rel_url`          | 文章相对于 `/post` 的路径                        |
| `unique_key`       | 文章的唯一标记值，同时也是页面的绝对路径（不包含 application root） |
| `layout`           | 布局                                       |
| `title`            | 标题                                       |
| `author`           | 作者                                       |
| `email`            | 作者 email                                 |
| `tags`             | 标签列表                                     |
| `categories`       | 分类列表                                     |
| `created`          | 创建时间                                     |
| `updated`          | 更新时间                                     |
| `preview`          | 预览部分解析后的 HTML 内容（只在获取文章列表时有）             |
| `has_more_content` | 除了预览部分之外是否正文很有更多内容（只在获取文章列表时有）           |
| `content`          | 全部正文解析后的 HTML 内容（只在获取单个文章时有）             |

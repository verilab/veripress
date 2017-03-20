---
title: 开始使用
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 的使用以一个实例（instance）为单位，比如你使用它搭建一个博客，这个博客就是一个实例。一个实例的所有相关文件都保存在一个目录中，可以很方便地管理。

## 创建实例

首先在适当的位置创建一个目录，通常情况下空目录就可以，如果你使用 virtualenv，也可以在里面先创建虚拟环境。

然后 cd 进入这个目录，执行初始化命令，如：

```sh
$ mkdir my-veripress
$ cd my-veripress
$ veripress init
```

如果你想在系统的其它位置也能控制这个实例，可以设置环境变量 `VERIPRESS_INSTANCE_PATH` 为你想控制的实例的绝对路径，例如：

```sh
$ export VERIPRESS_INSTANCE_PATH=/home/user/my-veripress
```

之后你就可以在其他目录执行 `veripress` 命令来控制这个实例。

## 初始目录结构

上面的初始化命令将会在实例目录创建若干子目录和文件：

| 文件／子目录      | 作用                     |
| ----------- | ---------------------- |
| `config.py` | 实例的配置文件                |
| `site.json` | 网站信息                   |
| `static`    | 全局的静态文件（默认有一个 favicon） |
| `themes`    | 存放主题                   |
| `posts`     | 存放文章（post）             |
| `pages`     | 存放自定义页面（page）          |
| `widgets`   | 存放页面部件（widget）         |

## 修改网站信息

网站的标题、作者等信息在 `site.json`，用 JSON 格式编写，你可以自行修改。

每一项的说明如下：

| 项        | 说明                                       |
| -------- | ---------------------------------------- |
| title    | 网站标题                                     |
| subtitle | 网站副标题，对于支持副标题的主题有效                       |
| author   | 网站作者，若文章和页面没有标注作者，则默认使用此项                |
| email    | 网站作者 email，若文章和页面没有标注作者 email，则默认使用此项    |
| timezone | 可选，用于在生成 Atom 订阅时指定时区，格式类似 `UTC+08:00`   |
| root_url | 可选，指定网站的根 URL，不要加结尾的 `/`，如果网站在子目录中，请不要加子目录，如网站在 `http://example.com/blog/` 则填写 `http://example.com`，此项用于生成某些评论框所需的页面完整链接，如不需要评论框，可以不填 |

## 安装默认主题

初始化之后的实例默认使用 default 主题，因此必须首先安装 default 主题才可以运行网站。使用下面命令安装（此命令需要系统中安装有 Git）：

```sh
$ veripress theme install default
```

它将从官方的 [veripress/themes](https://github.com/veripress/themes) 仓库中安装 default 主题。关于主题的更多信息，请参考 [主题](theme.html)。

## 预览网站

安装主题之后，就可以预览网站了，使用下面命令：

```sh
$ veripress preview
```

默认将会在 `127.0.0.1:8080` 开启一个 HTTP 服务器，可以通过 `--host` 和 `--port` 来修改，例如：

```sh
$ veripress preview --host 0.0.0.0 --port 8000
```

此时你已经可以通过浏览器访问 `http://127.0.0.1:8080/` 了，可以看到默认的《Hello, world!》文章以及侧边栏上默认的《Welcome!》页面部件，访问 `http://127.0.0.1:8080/hello/` 可以看到一个默认的自定义页面，这三者分别在 `posts`、`widgets`、`pages` 目录中。

## 添加你的第一篇文章！

在 `posts` 目录创建一个新的文件，按照 `2017-03-20-my-first-post.md` 的格式命名，这里我们以 Markdown 为例，所以使用 `.md` 扩展名。

添加内容如下：

```md
---
title: 我的第一篇文章！
---

## 这是标题

一段文字……
```

然后重新运行 `veripress preview` 即可看到这篇文章。

关于如何撰写文章、自定义页面、页面部件的更多信息，请参考 [撰写内容](writing.html)。

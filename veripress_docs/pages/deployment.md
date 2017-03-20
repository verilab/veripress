---
title: 部署网站
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

有多种方式可以用来部署 VeriPress 站点，具体使用哪种，取决于你的使用环境和使用习惯。

## 静态部署

### 生成静态页面

通过 `veripress generate` 命令，可以在 VeriPress 实例的 `_deploy` 目录中生成网站的所有静态文件、页面。如果 `_deploy` 目录已存在且不为空，则会首先**清除该目录中的非隐藏文件**，或者说非 `.` 开头的文件（因为在 Windows 上这些并不一定是隐藏文件）。

`generate` 命令还会提示你输入一个「application root」，这个也就是网站的子目录路径，例如，如果你的网站打算跑在 `http://example.com/blog/`，则这里你需要填 `/blog/`，而如果跑在 `http://example.com/`，则这里保持默认的 `/`。

另外，对于自定义页面（page），VeriPress 目前的策略是先将所有 `pages` 的文件复制，然后将其中的自定义页面解析成 HTML，同时原始文件保留，这里存在一个悖论，就是如果生成的静态页面是开源的，但又存在 `is_draft` 为 `true` 的页面，那这个页面的原始文件仍然可以被看到，而如果不保留原始文件，那如果这个文件本身就不应该看作是自定义页面，而是另一个自定义页面所链接的资源，就会无法访问这个文件。目前保留这个策略是因为我觉得前者出现的可能性要比后者小，如果实际的使用中出现一些必要的理由或者更好的解决解决办法，这个策略可能会进行调整。

### 部署到 GitHub Pages

生成了静态页面之后你可以在各种地方部署，很多人会将静态页面部署在 GitHub Pages，因此 VeriPress 在命令行界面中加入了命令来简化这个操作。

首先你需要在 GitHub 创建一个仓库用来存放页面，假设你的 GitHub 账号是 username，则可以创建一个名为 `username.github.io` 的仓库，这个仓库将可以通过 `https://username.github.io/` 直接访问，而如果创建其它名称的仓库，假设 my-blog，则可以通过 `https://username.github.io/my-blog/` 访问（这种情况下，你就需要使用 `/my-blog/` 作为生成静态页面时的「application root」）

然后运行下面命令（这里假设你已经在系统中生成 SSH key 并添加到 GitHub，如果没有，请参考 [Connecting to GitHub with SSH](https://help.github.com/articles/connecting-to-github-with-ssh/)）：

```sh
$ veripress setup-github-pages
 Please enter your GitHub repo name, e.g. "someone/the-repo": username/blog
 Please enter your name (for git config): User Name
 Please enter your email (for git config): username@example.com
 Initialized empty Git repository in /root/a/_deploy/.git/
$ veripress deploy
```

即可将前面生成的静态页面部署到 GitHub 仓库。之后你可能还需要在 GitHub 仓库的「Settings」中，将 GitHub Pages 的「Source」设置为「master branch」。

如果 `deploy` 命令不能符合你的需求，你也可以自己使用 `git` 命令来操作，效果是一样的。

## 动态部署

### serve 命令

动态部署也就是直接运行 Python web app。默认提供了 `serve` 命令来进行动态部署，使用方式如下：

```sh
$ veripress serve --host 0.0.0.0 --port 8000
```

不加参数的情况下默认监听 `127.0.0.1:8080`。

这个命令会首先尝试使用 `gevent.wsgi` 包的 `WSGIServer` 来运行，如果你系统中没有安装 gevent，则会使用 Flask app 的 run 方法。后者是用在开发环境的方法，不应该实际应用中使用，所以如果你打算使用 `serve` 命令部署，则应该先安装 gevent：

```sh
$ pip install gevent
```

### 使用其它 WSGI 服务器

VeriPress 主 app 对象在 `veripress` 包中，由于基于 Flask，这个 app 对象直接是一个 WSGI app，所以你可以使用任何可以部署 WSGI app 的服务器来部署 VeriPress 实例，例如使用 Gunicorn（需要在 VeriPress 实例目录中执行，或设置 `VERIPRESS_INSTANCE_PATH` 环境变量）：

```sh
$ gunicorn -b 0.0.0.0:8000 veripress:app
```

其它更多部署方法请参考 Flask 官方文档的 [Deployment Options](http://flask.pocoo.org/docs/0.12/deploying/)。

## 缓存

动态部署时 VeriPress 可以使用缓存来加快页面的访问，具体的配置方法请参考 [配置文件](configuration-file.html#CACHE-TYPE)。

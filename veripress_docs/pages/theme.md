---
title: 主题
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 原生支持主题切换，通过配置文件的 `THEME` 配置项来指定要使用的主题，内部通过这个配置项，来渲染相应主题目录中的模板文件。与此同时，`veripress` 命令还提供了方便的主题管理系列子命令。

## 安装官方主题

目前官方主题有 default、clean-doc 等，可以在 [veripress/themes](https://github.com/veripress/themes) 查看最新的官方主题列表和预览（或截图）。

要安装官方主题，使用如下命令：

```sh
$ veripress theme install theme-name  # theme-name 换成要安装的主题名称
```

这个命令会使用 Git 将 [veripress/themes](https://github.com/veripress/themes) 仓库中与指定的主题名同名的分支克隆到本地的 `themes` 目录，并默认使用同样的名字作为本地的主题名称。例如，上面给出的命令将把 [veripress/themes](https://github.com/veripress/themes) 的 theme-name 分支克隆到本地的 `themes/theme-name` 目录。

如果你想在本地使用不同的主题名，比如把官方的 clean-doc 安装为本地的 doc 主题，那么可以使用 `--name` 参数来指定，如：

```sh
$ veripress theme install clean-doc --name doc
```

这将会把 clean-doc 主题安装到 `themes/doc` 目录，从而你可以把配置文件的 `THEME` 设置为 `doc` 来使用它，而不是 `clean-doc`。

## 安装第三方主题

`veripress theme install` 命令同样可以用来安装 GitHub 上的第三方主题，例如你想安装的主题在 someone/the-theme 仓库（的 master 分支），则可以使用下面命令来安装它：

```sh
$ veripress theme install someone/the-theme
```

不加参数的情况下，会把 master 分支克隆到 `themes`，并以 `the-theme` 作为本地主题名称。你可以通过 `--branch` 和 `--name` 参数指定分支和名称：

```sh
$ veripress theme install someone/the-theme --branch the-branch --name theme-name
```

上面命令会把 someone/the-theme 仓库的 the-branch 分支克隆到 `themes/theme-name` 目录，从而可以将 `THEME` 设置为 `theme-name` 来使用它。

## 更新和删除主题

下面两条命令分别可以更新和删除已安装的主题：

```sh
$ veripress theme update theme-name
$ veripress theme uninstall theme-name
```

前者相当于执行了 `git pull`，后者相当于删除了 `themes` 目录中的相应主题子目录。

另外，已经安装的所有主题可以通过 `veripress theme list` 列出。

## 在已有主题的基础上自定义

由于主题是一个通用化的东西，可能你在使用的时候需要进行个性化的简单定制，例如修改导航栏、使用自定义布局等。

通常，主题的作者在制作主题时，会允许用户将自己的模板文件放在主题目录的 `custom` 子目录中，来覆盖主题本身的同名模板文件，而不影响该主题原先的代码，从而不影响后期的主题更新。此外，VeriPress 在渲染模板文件时，也会优先使用 `custom` 子目录中的同名模板文件。

下面先给出两种使用场景，关于模板文件具体如何编写，请参考 [制作主题](making-your-own-theme.html) 和 Jinja2 模板引擎的 [设计文档](http://jinja.pocoo.org/docs/2.9/templates/)。

### 修改主题模板的某一部分

主题的模板文件中通常使用类似 `include` 的语句来引入每个小部分，以 default 主题为例，它的 `layout.html` 模板中有一行：

```
{% include ['custom/navbar.html', 'navbar.html'] ignore missing %}
```

这行会优先引入 `custom` 中的 `navbar.html`，如果不存在，则使用主题自带的。因此你可以在 `custom` 中创建自定义的 `navbar.html`，来添加你需要的导航栏项。

### 在文章或页面中使用自定义布局

还记得文章和页面的 YAML 头部的 `layout` 项吗，默认分别为 `post` 和 `page`，对应主题的 `post.html` 和 `page.html` 模板文件。如果你需要自定义，则可以在主题的 `custom` 目录中创建新的布局的模板文件。

例如你需要一个新的名叫 `simple-page` 的布局，就新建模板文件 `custom/simple-page.html`，假设内容如下：

```html
<!DOCTYPE html>
<html>
<head>
  <title>{{ entry.title + ' - ' + site.title }}</title>
</head>
<body>
  <div class="content">{{ entry.content|safe }}</div>
</body>
</html>
```

此时你就可以在自定义页面中指定 `layout` 为 `simple-page`，从而使用上面的模板来显示这个页面，如：

```
---
title: 一个简单页面
layout: simple-page
---

这是一个非常简单的页面。
```

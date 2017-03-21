---
title: 安装
author: Richard Chien
created: 2017-03-19
updated: 2017-03-20
---

要使用 VeriPress，你的电脑上需要安装有 Python 3.4 或更新版本和 pip 命令。如果你的系统中同时安装有 Python 2.x 版本，你可能需要将下面的 `python` 和 `pip` 命令换成 `python3` 和 `pip3`，此外对于非 root 或非管理员用户，还需要加 `sudo` 或使用管理员身份启动命令行。

## 系统全局安装

使用 pip 命令即可从 PyPI 上安装最新的 release 版本：

```sh
$ pip install veripress
```

安装之后一个 `veripress` 命令会被安装在系统中，通常在 `/usr/local/bin/veripress`。在命令行中运行 `veripress --help` 可以查看命令的使用帮助，当然，如果这是你第一次使用，你可能更需要首先阅读后面的 [开始使用](getting-started.html) 文档。

## 在 virtualenv 中安装

由于安装 VeriPress 的同时会安装一些依赖包，你可能不希望这些依赖装到系统的全局环境，这种情况下，使用 virtualenv 创建一个虚拟环境是一种不错的选择。

如果你还没有安装 virtualenv，请使用下面命令安装：

```sh
$ pip install virtualenv
```

然后到一个适当的目录，运行下列命令：

```sh
$ mkdir my-veripress
$ cd my-veripress
$ virtualenv venv
```

这将会在 `venv` 文件夹中创建一个虚拟环境，要使用这个虚拟环境，运行如下：

```sh
$ source venv/bin/activate  # Linux or macOS
$ venv\Scripts\activate  # Windows
```

然后安装 VeriPress：

```sh
$ pip install veripress
```

要退出虚拟环境，运行：

```sh
$ deactivate
```

在 virtualenv 中使用可以获得一个隔离的环境，但同时也需要多余的命令来进入和离开虚拟环境，因此你需要根据情况选择适合自己的安装方式。

## 在 Windows 上安装

在 Windows 上安装 VeriPress 没有什么特殊要求，只要正确安装了 Python 和 pip，就可以正常使用 `pip install veripress` 来安装，同样你也可以使用 virtualenv。

但由于 Windows 的特殊性，如果你在安装和之后的使用过程中遇到了问题，请提交 issue 反馈。

此外，后面的文档中给出的示例命令将会统一使用 Unix 命令，一般在 Windows 上都有相对应的命令可以完成同样的操作（比如创建文件夹）。

## 使用 Docker

VeriPress 官方提供了简便易用的 docker 镜像，如果你的系统中安装了 docker，并且希望在比较隔离的环境中使用 VeriPress，可以考虑通过 docker 来安装。直接拉取 DockerHub 的镜像：

```sh
$ docker pull veripress/veripress
```

镜像的最新版本（latest）将和 GitHub 上最新的 tag 一致，同时也和 PyPI 上的最新版本一致。

使用方式如下：

```sh
$ docker run -ti --rm -v $(pwd):/instance veripress/veripress --help
```

这将会把当前目录挂载到容器中的 `/instance` 目录，作为 VeriPress 的实例目录（在下一篇 [开始使用](getting-started.html) 中你将会了解到什么是「实例目录」。镜像的 `ENTRYPOINT` 是 `veripress` 命令，因此直接在 `docker run` 命令的结尾加上 `veripress` 的子命令即可使用，在后面的文档中将不再对 docker 进行单独阐述，使用方式都是一致的。

建议把 `docker run -ti --rm -v $(pwd):/instance veripress/veripress` alias 成一个简短的命令，这样可以更方便的使用（基本和使用本地命令没差）。另外，在要运行 VeriPress 实例时，需要加 `-p` 来进行端口映射。

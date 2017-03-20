---
title: Webhook
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 支持通过接收 webhook 回调来在某些特定外部事件发生时执行自定义 Python 脚本，从而实现例如 GitHub 仓库发生 push 事件就自动拉取最新内容这样的用法。

无论运行模式是 `api-only` 还是 `view-only` 还是 `mixed`，`/_webhook` 这个 URL 都可以接收 POST 请求。收到请求后，它会在 VeriPress 实例目录中寻找 `webhook.py` 文件，如果存在，则会在 Flask 的 request context 下执行这个文件的代码（此为同步执行，如果需要进行长时间的任务，最好开新的线程或进程），不存在则跳过。无论该脚本存在与否最终都返回 `204 NO CONTENT`。

「在 Flask 的 request context 下执行」意味着在脚本中可以访问到 Flask 当前请求的 `request` 对象、`g` 对象、`current_app` 对象，也就是说你可以在这里对 POST 请求进行鉴权、使用甚至修改 app 的配置文件等。关于 Flask 的 request context，请参考 Flask 官方文档的 [The Request Context](http://flask.pocoo.org/docs/0.12/reqcontext/)。

一段可能的自定义脚本如下：

```py
import os
from flask import request
from veripress import cache

def check_token():
    # 对请求进行鉴权，防止恶意请求
    return True

if check_token():
    os.system('git pull')
    cache.clear()
```

---
title: Webhook
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 支持通過接收 webhook 回呼來在某些特定外部事件發生時執行自訂 Python 腳本，從而實現例如 GitHub 倉庫發生 push 事件就自動拉取最新內容這樣的用法。

無論運行模式是 `api-only` 還是 `view-only` 還是 `mixed`，`/_webhook` 這個 URL 都可以接收 POST 請求。收到請求後，它會在 VeriPress 實例目錄中尋找 `webhook.py` 檔，如果存在，則會在 Flask 的 request context 下執行這個檔的代碼（此為同步執行，如果需要進行長時間的任務，最好開新的執行緒或進程），不存在則跳過。無論該腳本存在與否最終都返回 `204 NO CONTENT`。

「在 Flask 的 request context 下執行」意味著在腳本中可以訪問到 Flask 當前請求的 `request` 物件、`g` 物件、`current_app` 物件，也就是說你可以在這裡對 POST 請求進行鑒權、使用甚至修改 app 的設定檔等。關於 Flask 的 request context，請參考 Flask 官方文檔的 [The Request Context](http://flask.pocoo.org/docs/0.12/reqcontext/)。

一段可能的自訂腳本如下：

```py
import os
from flask import request
from veripress import cache

def check_token():
    # 對請求進行鑒權，防止惡意請求
    return True

if check_token():
    os.system('git pull')
    cache.clear()
```

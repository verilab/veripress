---
title: 部署網站
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

有多種方式可以用來部署 VeriPress 網站，具體使用哪種，取決於你的使用環境和使用習慣。

## 靜態部署

### 生成靜態頁面

通過 `veripress generate` 命令，可以在 VeriPress 實例的 `_deploy` 目錄中生成網站的所有靜態檔、頁面。如果 `_deploy` 目錄已存在且不為空，則會首先**清除該目錄中的非隱藏檔**，或者說非 `.` 開頭的檔（因為在 Windows 上這些並不一定是隱藏檔）。

`generate` 命令還會提示你輸入一個「application root」，這個也就是網站的子目錄路徑，例如，如果你的網站打算跑在 `http://example.com/blog/`，則這裡你需要填 `/blog/`，而如果跑在 `http://example.com/`，則這裡保持默認的 `/`。

另外，對於自訂頁面（page），VeriPress 目前的策略是先將所有 `pages` 的檔複製，然後將其中的自訂頁面解析成 HTML，同時原始檔保留，這裡存在一個悖論，就是如果生成的靜態頁面是開源的，但又存在 `is_draft` 為 `true` 的頁面，那這個頁面的原始檔仍然可以被看到，而如果不保留原始檔，那如果這個檔本身就不應該看作是自訂頁面，而是另一個自訂頁面所連結的資源，就會無法訪問這個檔。目前保留這個策略是因為我覺得前者出現的可能性要比後者小，如果實際的使用中出現一些必要的理由或者更好的解決解決辦法，這個策略可能會進行調整。

### 部署到 GitHub Pages

生成了靜態頁面之後你可以在各種地方部署，很多人會將靜態頁面部署在 GitHub Pages，因此 VeriPress 在命令列介面中加入了命令來簡化這個操作。

首先你需要在 GitHub 創建一個倉庫用來存放頁面，假設你的 GitHub 帳號是 username，則可以創建一個名為 `username.github.io` 的倉庫，這個倉庫將可以通過 `https://username.github.io/` 直接訪問，而如果創建其它名稱的倉庫，假設 my-blog，則可以通過 `https://username.github.io/my-blog/` 訪問（這種情況下，你就需要使用 `/my-blog/` 作為生成靜態頁面時的「application root」）

然後運行下面命令（這裡假設你已經在系統中生成 SSH key 並添加到 GitHub，如果沒有，請參考 [Connecting to GitHub with SSH](https://help.github.com/articles/connecting-to-github-with-ssh/)）：

```sh
$ veripress setup-github-pages
 Please enter your GitHub repo name, e.g. "someone/the-repo": username/blog
 Please enter your name (for git config): User Name
 Please enter your email (for git config): username@example.com
 Initialized empty Git repository in /root/a/_deploy/.git/
$ veripress deploy
```

即可將前面生成的靜態頁面部署到 GitHub 倉庫。之後你可能還需要在 GitHub 倉庫的「Settings」中，將 GitHub Pages 的「Source」設置為「master branch」。

如果 `deploy` 命令不能符合你的需求，你也可以自己使用 `git` 命令來操作，效果是一樣的。

## 動態部署

### serve 命令

動態部署也就是直接運行 Python web app。預設提供了 `serve` 命令來進行動態部署，使用方式如下：

```sh
$ veripress serve --host 0.0.0.0 --port 8000
```

不加參數的情況下預設監聽 `127.0.0.1:8080`。

這個命令會首先嘗試使用 `gevent.wsgi` 包的 `WSGIServer` 來運行，如果你系統中沒有安裝 gevent，則會使用 Flask app 的 run 方法。後者是用在開發環境的方法，不應該實際應用中使用，所以如果你打算使用 `serve` 命令部署，則應該先安裝 gevent：

```sh
$ pip install gevent
```

### 使用其它 WSGI 伺服器

VeriPress 主 app 物件在 `veripress` 包中，由於基於 Flask，這個 app 物件直接是一個 WSGI app，所以你可以使用任何可以部署 WSGI app 的伺服器來部署 VeriPress 實例，例如使用 Gunicorn（需要在 VeriPress 實例目錄中執行，或設置 `VERIPRESS_INSTANCE_PATH` 環境變數）：

```sh
$ gunicorn -b 0.0.0.0:8000 veripress:app
```

其它更多部署方法請參考 Flask 官方文檔的 [Deployment Options](http://flask.pocoo.org/docs/0.12/deploying/)。

## 緩存

動態部署時 VeriPress 可以使用緩存來加快頁面的訪問，具體的配置方法請參考 [設定檔](configuration-file.html#CACHE-TYPE)。

---
title: 開始使用
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 的使用以一個實例（instance）為單位，比如你使用它搭建一個博客，這個博客就是一個實例。一個實例的所有相關檔都保存在一個目錄中，可以很方便地管理。

## 創建實例

首先在適當的位置創建一個目錄，通常情況下空目錄就可以，如果你使用 virtualenv，也可以在裡面先創建虛擬環境。

然後 cd 進入這個目錄，執行初始化命令，如：

```sh
$ mkdir my-veripress
$ cd my-veripress
$ veripress init
```

如果你想在系統的其它位置也能控制這個實例，可以設置環境變數 `VERIPRESS_INSTANCE_PATH` 為你想控制的實例的絕對路徑，例如：

```sh
$ export VERIPRESS_INSTANCE_PATH=/home/user/my-veripress
```

之後你就可以在其他目錄執行 `veripress` 命令來控制這個實例。

## 初始目錄結構

上面的初始化命令將會在實例目錄創建若干子目錄和檔：

| 檔／子目錄      | 作用                     |
| ----------- | ---------------------- |
| `config.py` | 實例的設定檔                |
| `site.json` | 網站信息                   |
| `static`    | 全域的靜態檔（預設有一個 favicon） |
| `themes`    | 存放主題                   |
| `posts`     | 存放文章（post）             |
| `pages`     | 存放自訂頁面（page）          |
| `widgets`   | 存放頁面部件（widget）         |

## 修改網站資訊

網站的標題、作者等資訊在 `site.json`，用 JSON 格式編寫，你可以自行修改。

每一項的說明如下：

| 項          | 說明                                       |
| ---------- | ---------------------------------------- |
| `title`    | 網站標題                                     |
| `subtitle` | 網站副標題，對於支援副標題的主題有效                       |
| `author`   | 網站作者，若文章和頁面沒有標注作者，則默認使用此項                |
| `email`    | 網站作者 email，若文章和頁面沒有標注作者 email，則默認使用此項    |
| `timezone` | 可選，用於在生成 Atom 訂閱時指定時區，格式類似 `UTC+08:00`   |
| `root_url` | 可選，指定網站的根 URL，不要加結尾的 `/`，如果網站在子目錄中，請不要加子目錄，如網站在 `http://example.com/blog/` 則填寫 `http://example.com`，此項用於生成某些評論框所需的頁面完整連結，如不需要評論框，可以不填 |

## 安裝預設主題

初始化之後的實例預設使用 default 主題，因此必須首先安裝 default 主題才可以運行網站。使用下面命令安裝（此命令需要系統中安裝有 Git）：

```sh
$ veripress theme install default
```

它將從官方的 [veripress/themes](https://github.com/veripress/themes) 倉庫中安裝 default 主題。關於主題的更多資訊，請參考 [主題](theme.html)。

## 預覽網站

安裝主題之後，就可以預覽網站了，使用下面命令：

```sh
$ veripress preview
```

默認將會在 `127.0.0.1:8080` 開啟一個 HTTP 伺服器，可以通過 `--host` 和 `--port` 來修改，例如：

```sh
$ veripress preview --host 0.0.0.0 --port 8000
```

此時你已經可以通過流覽器訪問 `http://127.0.0.1:8080/` 了，可以看到默認的《Hello, world!》文章以及側邊欄上默認的《Welcome!》頁面部件，訪問 `http://127.0.0.1:8080/hello/` 可以看到一個預設的自訂頁面，這三者分別在 `posts`、`widgets`、`pages` 目錄中。

## 添加你的第一篇文章！

在 `posts` 目錄創建一個新的檔，按照 `2017-03-20-my-first-post.md` 的格式命名，這裡我們以 Markdown 為例，所以使用 `.md` 副檔名。

添加內容如下：

```md
---
title: 我的第一篇文章！
---

## 這是標題

一段文字……
```

然後重新運行 `veripress preview` 即可看到這篇文章。

關於如何撰寫文章、自訂頁面、頁面部件的更多資訊，請參考 [撰寫內容](writing.html)。

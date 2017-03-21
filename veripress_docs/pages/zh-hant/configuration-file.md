---
title: 設定檔
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

`config.py` 檔即 VeriPress 的設定檔，初始化實例之後會生成一份預設的配置，多數情況下，你可能需要秀改設定檔來符合個性化的需求，同時，設定檔可以被主題範本獲取到，因此某些主題可能會對設定檔的某些項的不同配置表現出不同的行為。

下面給出 VeriPress 和預設主題所支援的配置項的說明（對於協力廠商主題特定的配置項要求，請參考它們的作者給出的使用方式）。

## STORAGE_TYPE

指定內容的存儲方式。

VeriPress 在設計時允許了未來加入不同的存儲方式（比如資料庫存儲），而不限於使用檔存儲。不過目前只支援檔存儲，所以此項應該填默認的 `file`。

## THEME

指定要使用的主題。

預設為 `default`，即使用 default 主題，如果你安裝了其它主題，就可以修改這個配置來更換主題，比如你現在看到的文檔使用了 clean-doc 主題，可以使用 `veripress theme install clean-doc` 安裝。

## CACHE_TYPE

指定緩存類型。

預設的 `simple` 表示使用簡單的記憶體緩存。VeriPress 的緩存使用了 Flask-Caching 擴展，支援如下類型：

| 配置值             | 說明                |
| --------------- | ----------------- |
| `null`          | 不使用緩存             |
| `simple`        | 簡單記憶體緩存            |
| `memcached`     | Memcached 緩存      |
| `gaememcached`  | GAE memcached 緩存  |
| `saslmemcached` | SASL memcached 緩存 |
| `redis`         | Redis 緩存          |
| `filesystem`    | 檔案系統緩存            |

對於除了 `null`、`simple` 之外的配置，還需要提供其它所需的配置項，例如使用 `redis` 則需要另外提供 `CACHE_REDIS_HOST`、`CACHE_REDIS_PORT` 等，請參考 Flask-Caching 的文檔 [Configuring Flask-Caching](https://pythonhosted.org/Flask-Caching/#configuring-flask-caching)。

## MODE

指定運行模式。

VeriPress 支援三種運行模式：`view-only`、`api-only`、`mixed`。`view-only` 表示只能訪問頁面，無法通過 API 直接獲取 JSON 資料；`api-only` 表示只能通過 API 獲取 JSON 資料；`mixed`，顧名思義，前兩者混合模式。

關於 API 模式的更多資訊，請參考 [API 模式](api-mode.html)。

## ENTRIES_PER_PAGE

指定首頁文章清單每頁顯示的文章數量。

預設情況下網站的首頁是文章（post）列表，並通過 URL `/page/<page_num>/` 來分頁，因此需要指定每頁顯示的文章數量。對於會顯示內容預覽的主題，這個值可以設置小一些，而不顯示預覽的主題，可以設置大一些。

## FEED_COUNT

指定 Atom 訂閱中的文章數量。

例如設置為 10 則 Atom 訂閱中只會生成最新的 10 篇文章。

## SHOW_TOC

指定是否顯示 TOC（目錄）。

實際上此配置項是控制 VeriPress 內部是否生成 TOC，如果設置成 `False` 則主題範本無法收到 TOC。相反，設置成 `True` 則主題範本可以收到一個 TOC 清單和 TOC HTML 字串，但是否顯示最終取決於主題。

## TOC_DEPTH 和 TOC_LOWEST_LEVEL

指定 TOC 的最大深度和最低標題級別。

這兩個範圍都是 1～6，兩個含義有一定區別。首先給一個 HTML 的示例：

```html
<h6>Title 1</h6>
<h1>Title 2</h1>
  <h2>Title 3</h2>
    <h4>Title 4</h4>
    <h3>Title 5</h3>
<h1>Title 6</h1>
  <h5>Title 7</h5>
```

對於上面的示例，在不限最大深度和最低標題級別的情況下，生成的 TOC 應該和給出的縮進相同。可以發現 Title 1 也在生成的 TOC 中，如果想過濾掉這種級別比較低的標題，可以設置 `TOC_LOWEST_LEVEL` 為比較小的值，比如設置為 4，則 `h5`、`h6` 標籤都不會算在內。同時可以發現這個 TOC 有三層，如果只需要顯示兩層，可以將 `TOC_DEPTH` 設置為 2。

## ALLOW_SEARCH_PAGES

指定是否允許搜索自訂頁面的內容。

只在動態運行時有效（生成靜態檔之後沒法搜索）。設置為 `False` 則在搜索時不會搜索自訂頁面的內容。另外，只支援搜索 VeriPress 中解析器所支援的格式中的文字，例如使用 Markdown 編寫的自訂頁面，相反地，直接的 HTML 檔或其它靜態檔無法被搜索到。

## DUOSHUO_ENABLED、DUOSHUO_SHORT_NAME、DISQUS_ENABLED 和 DISQUS_SHORT_NAME

指定是否開啟多說或 Disqus 評論框，以及它們的 shortname。

default 主題和 clean-doc 主題支援多說和 Disqus 評論框，例如設置：

```py
DISQUS_ENABLED = True
DISQUS_SHORT_NAME = 'your-shorname'
```

將會在文章和自訂頁面底部顯示 Disqus 評論框，多說同理。

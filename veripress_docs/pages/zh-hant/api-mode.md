---
title: API 模式
author: Richard Chien
created: 2017-03-20
updated: 2017-03-21
---

當運行模式 `MODE` 設置為 `api-only` 或 `mixed` 時，即開啟了 API 模式，這種情況下，可以通過 `/api` 首碼來訪問 API，由此將可以不受 VeriPress 頁面劃分邏輯的限制（只有首頁的文章列表可以分頁，標籤、分類、歸檔、搜尋網頁面默認不分頁，這些限制是為了保持動態和靜態運行的體驗一致性），而直接在前端去獲取資料並按想要的方式顯示。

## 基礎知識

### API 可以獲取什麼？

API 模式開放的這些 API，只能獲取和頁面上顯示的同樣的文章清單、自訂頁面和頁面部件等，也就是說，設置為草稿的內容將無法獲取到。同時目前也無法獲取自訂頁面的清單（因為這一內容形式變化性比較強，暫時沒有較好的辦法提供 API），只能通過具體路徑獲取單個頁面。

另外，在獲取文章列表時，返回的結果只有預覽部分，獲取單個文章時，則返回全部正文內容。

### API 的請求方式

所有 API 均使用 GET 方式來請求，當 HTTP 回應碼為 200 時表示請求成功，這意味著請求的資源存在，並成功獲取，返回的 JSON 中將直接包含該資源的資料，在後面的 API 列表中分別給出。狀態碼 4xx 表示請求失敗，具體的錯誤狀態碼根據情況而不同，此時返回的 JSON 資料有 `code` 和 `message` 兩個欄位，分別是錯誤碼和錯誤資訊，例如：

```json
{
  "code": 101,
  "message": "No such API."
}
```

不同的 HTTP 狀態碼、錯誤碼對應錯誤原因如下表：

| 錯誤碼  | HTTP 狀態碼 | 錯誤原因        |
| ---- | -------- | ----------- |
| 100  | 400      | 未定義的錯誤      |
| 101  | 404      | API 不存在     |
| 102  | 404      | 資源不存在       |
| 103  | 400      | 請求參數不正確     |
| 104  | 403      | 請求的資源路徑不被允許 |
| 105  | 400      | 請求的資源路徑無法識別 |

## API 列表

### /api/site 獲取網站資訊

返回內容即為 `site.json` 的內容。

### /api/posts 獲取文章列表

可以接受的 URL 參數如下：

| 參數名                                      | 說明                                       |
| ---------------------------------------- | ---------------------------------------- |
| `title`、`layout`、`author`、`email`、`tags`、`categories` | 用於限定文章的元資訊，可以多選，用英文逗號分隔                  |
| `created`、`updated`                      | 用於限定創建和更新日期，每個參數必須是用逗號分隔的兩個值，格式如 `2017-03-20`，分別為開始日期和截止日期 |
| `start`                                  | 經過所有篩選之後，返回資料清單的第一個的下標                   |
| `count`                                  | 獲取的文章數量                                  |
| `fields`                                 | 指定要獲取的文章資訊的欄位名，可多選，用逗號分隔                 |

例如請求 `/api/posts?layout=post&tags=Hello,Greeting&created=2017-01-01,2017-03-20&start=10&count=10&fields=title,author,created,updated,preview` 將返回佈局為 `post`、有 `Hello` 或 `Greeting` 標籤、在 2017-01-01 到 2017-03-20 之間創建的所有文章的第 10 條到第 19 條的 `title`、`author`、`created`、`updated`、`preview` 欄位。

除了 URL 參數之外，還可以通過路徑來對返回結果進行篩選（注意這裡的篩選會在通過 `start` 和 `count` 參數取子列表之前進行），形如 `/api/posts/:year/:month/:day/:post_name`，四個路徑參數分別表示創建年份、月份、日期、文章名（不是標題，是顯示在 URL 中的文章名），可以從後往前依次省略。一旦指定了最後一個文章名，返回結果將不再是 JSON 陣列，而是單個文章的 JSON 對象。

如果按條件篩選、按 `start`、`count` 取子列表之後，結果是空，則會返回錯誤碼 102（資源不存在）。

資源存在時回應資料如下（沒有精確指定到文章名的情況，為一個 JSON 陣列）：

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

其中每個文章物件的欄位說明如下：

| 欄位名                | 說明                                       |
| ------------------ | ---------------------------------------- |
| `format`           | 撰寫文章所使用的格式                               |
| `is_draft`         | 是否草稿（API 所能獲取到的全為 false）                 |
| `meta`             | 文章的原始元資訊，保留了檔中的 YAML 頭解析之後的最原始資訊        |
| `rel_url`          | 文章相對於 `/post` 的路徑                        |
| `unique_key`       | 文章的唯一標記值，同時也是頁面的絕對路徑（不包含 application root） |
| `layout`           | 佈局                                       |
| `title`            | 標題                                       |
| `author`           | 作者                                       |
| `email`            | 作者 email                                 |
| `tags`             | 標籤列表                                     |
| `categories`       | 分類列表                                     |
| `created`          | 創建時間                                     |
| `updated`          | 更新時間                                     |
| `preview`          | 預覽部分解析後的 HTML 內容（只在獲取文章列表時有）             |
| `has_more_content` | 除了預覽部分之外是否正文很有更多內容（只在獲取文章列表時有）           |
| `content`          | 全部正文解析後的 HTML 內容（只在獲取單個文章時有）             |

### /api/tags 和 /api/categories 獲取標籤和分類列表

直接返回所有的標籤／分類和該標籤／分類下的非草稿（已發佈）文章數量，如：

```json
[
  {
    "name": "Programming Language",
    "published": 2
  },
  {
    "name": "Python",
    "published": 2
  },
  {
    "name": "Web Framework",
    "published": 1
  },
  {
    "name": "Flask",
    "published": 1
  }
]
```

### /api/widgets 獲取頁面部件清單

可以接受的 URL 參數如下：

| 參數名        | 說明          |
| ---------- | ----------- |
| `position` | 指定要獲取的部件的位置 |

回應資料：

```json
[
  {
    "content": "<h4>My Name</h4>\n<p>Welcome to my blog!</p>",
    "format": "markdown",
    "is_draft": false,
    "meta": {
      "order": 0,
      "position": "sidebar"
    },
    "order": 0,
    "position": "sidebar"
  },
  {
    "content": "<h4>Friend Links</h4>",
    "format": "markdown",
    "is_draft": false,
    "meta": {
      "order": 1,
      "position": "sidebar"
    },
    "order": 1,
    "position": "sidebar"
  }
]
```

欄位說明：

| 欄位名        | 說明                                  |
| ---------- | ----------------------------------- |
| `format`   | 撰寫頁面部件所使用的格式                        |
| `is_draft` | 是否草稿（API 所能獲取到的全為 false）            |
| `meta`     | 頁面部件的原始元資訊，保留了檔中的 YAML 頭解析之後的最原始資訊 |
| `position` | 頁面部件的位置                             |
| `order`    | 頁面部件的排序                             |
| `content`  | 正文解析後的 HTML 內容                      |

### /api/pages/:page_path 獲取自訂頁面

`page_path` 路徑參數表示要獲取的自訂頁面的相對路徑，也即在以 view 模式訪問時所使用的路徑，比如一個頁面可以從 `/a/b/c/d.html` 訪問到，則相對應的 API URL 就是 `/api/pages/a/b/c/d.html`。如果請求的路徑是一個直接存在的檔，將會直接返回這個檔，否則，對於使用所支援的格式撰寫的頁面，將返回解析之後的 JSON 對象。前面一種情況不用多說，檔是什麼樣就會怎麼發送，後一種情況的回應資料如下：

```json
{
  "author": "My Name",
  "content": "<p>Lorem ipsum dolor sit amet</p>",
  "created": "1970-01-01 00:00:00",
  "email": "someone@example.com",
  "format": "markdown",
  "is_draft": false,
  "layout": "page",
  "meta": {
    "created": "1970-01-01 00:00:00"
  },
  "rel_url": "about/",
  "title": "About",
  "unique_key": "/about/",
  "updated": "1970-01-01 00:00:00"
}
```

欄位說明：

| 欄位名          | 說明                                       |
| ------------ | ---------------------------------------- |
| `format`     | 撰寫頁面所使用的格式                               |
| `is_draft`   | 是否草稿（API 所能獲取到的全為 false）                 |
| `meta`       | 頁面的原始元資訊，保留了檔中的 YAML 頭解析之後的最原始資訊        |
| `rel_url`    | 頁面相對於 `/` 的路徑                            |
| `unique_key` | 頁面的唯一標記值，同時也是頁面的絕對路徑（不包含 application root） |
| `layout`     | 佈局                                       |
| `title`      | 標題                                       |
| `author`     | 作者                                       |
| `email`      | 作者 email                                 |
| `created`    | 創建時間                                     |
| `updated`    | 更新時間                                     |
| `content`    | 全部正文解析後的 HTML 內容                         |

### /api/search 搜索文章和頁面

通過 URL 參數 `q` 指定搜索關鍵字，將會對文章和頁面（搜尋網頁面需要設定檔中 `ALLOW_SEARCH_PAGES` 設置為 True）的標題和正文解析之後的 HTML 內容進行搜索，將搜索到的文章和頁面全部放在一個 JSON 陣列中返回，具體的每個物件的欄位，和上面的獲取文章清單和獲取自訂頁面相同（其中，文章物件中只有 `preview`，沒有 `content`）。

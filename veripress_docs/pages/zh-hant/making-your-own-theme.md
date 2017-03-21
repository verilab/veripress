---
title: 製作主題
author: Richard Chien
created: 2017-03-21
updated: 2017-03-21
---

VeriPress 原生支援主題，如果你對官方主題或其它協力廠商主題感到不滿意，同時也有一定的程式設計基本知識，你就可以自行製作自己的主題，也歡迎你把自己製作的主題發佈到網上和其他人一起分享。

## 主題的組成部分

主題主要包括靜態檔和範本檔，分別在 `static` 子目錄和 `templates` 子目錄。

`static` 中的檔，可以直接通過 `/static/:path` 來訪問，例如 `/static/style.css` 可以訪問到當前正在使用的主題的 `static/style.css` 檔，而如果當前主題的 `static` 目錄中並沒有 `style.css` 檔，則會去 VeriPress 實例的全域 `static` 目錄中尋找。

`templates` 中的範本檔，會在收到請求後按照所請求的內容渲染成最終的 HTML 頁面，必須存在的範本有 `index.html`、`archive.html`，這兩個分別對應首頁和歸檔頁；而如果文章和自訂頁面使用了預設的佈局（分別 `post` 和 `page`），則還必須有 `post.html`、`page.html`；此外，標籤、分類、搜索三個頁面在沒有單獨範本的情況下都預設使用 `archive.html`，如果你需要單獨定義這三類頁面，使用 `tag.html`、`category.html`、`search.html` 來命名。除了上面各個對應實際頁面的範本，還有一個 `404.html` 用於在找不到頁面的情況下渲染。

VeriPress 在尋找範本檔時，首先會查找主題的 `templates/custom` 目錄，如果在裡面找到了相應的範本，將使用它（使用者自訂的範本），如果沒找到，將使用 `templates` 中的範本。

## 範本引擎

VeriPress 使用 Jinja2 範本引擎，下面簡單介紹它的語法。

`{{ ... }}` 用來表示運算式，範本檔在渲染時會傳入一些值（後面解釋），這些值可以通過形如 `{{ some_object.some_attribute }}` 的運算式來取出，運算式的計算結果將會轉成 HTML 顯示在相應的位置。

`{% ... %}` 用來表示語句，比如判斷語句、迴圈語句等，通過多個這樣的塊將語句主體包在中間，例如一個判斷結構：

```html
{% if True %}
  <p>{{ some_variable }}</p>
{% endif %}
```

限於篇幅這裡也不重複太多 Jinja2 的文檔了，具體的語法請參考 [Template Designer Documentation](http://jinja.pocoo.org/docs/2.9/templates/)。

下面將解釋渲染範本時「傳入的值」。

## 渲染範本的 Context

渲染範本時有個概念叫 context，也就是在範本渲染時可以接觸到的 Python 環境中的函數、物件等。由於基於 Flask，因此所有 Flask 的 context，都可以使用，例如 `request`、`config`、`session`、`url_for()` 等，通過這些，便可以訪問到當前的請求 URL、參數、設定檔等，可以參考 [Standard Context](http://flask.pocoo.org/docs/0.12/templating/#standard-context)。

除了 Flask 提供的這些，對於不同的範本檔，VeriPress 還提供了該範本可能會需要用到的物件，如下表：

| 範本              | 額外的 Context 物件                          | 說明                                       |
| --------------- | --------------------------------------- | ---------------------------------------- |
| `index.html`    | `entries`、`next_url`、`prev_url`         | 分別是當前分頁上的文章列表、下一頁的 URL、上一頁的 URL          |
| `post.html`     | `entry`                                 | 當前訪問的文章                                  |
| `page.html`     | `entry`                                 | 當前訪問的自訂頁面                               |
| `archive.html`  | `entries`、`archive_type`、`archive_name` | 分別是當前歸檔的文章列表、歸檔類型、歸檔名稱，其中 `/archive/` 頁面的歸檔類型為 `Archive`，名稱為 `All` 或類似 `2017`、`2017.3`（分別對應 `/archive/2017/` 和 `/archive/2017/03/` 頁面） |
| `tag.html`      | 同上                                      | 歸檔類型為 `Tag`，歸檔名稱為標籤名                     |
| `category.html` | 同上                                      | 歸檔類型為 `Category`，歸檔名稱為分類名                |
| `search.html`   | 同上                                      | 歸檔類型為 `Search`，歸檔名稱為搜索關鍵字加引號             |

以上的「文章」「自訂頁面」的資料，基本上和 [API 模式](api-mode.html#api-posts-獲取文章列表) 獲取到的相似，不同之處在於此處每個物件都多了一個 `url` 欄位，可以用來直接構造連結。

除了上述的每個範本不同的 context 物件，每個範本內都可以訪問 `site` 和 `storage` 兩個物件，前者即 `site.json` 中的內容，後者是當前使用的存儲類型的資料訪問封裝物件，一般很少會直接用這個，只有在獲取頁面部件時有必要使用（因為不是所有頁面都需要顯示部件，何時顯示由主題決定）。由於 `storage` 獲取到的資料是最原始的文章、頁面、部件的物件，這裡不再花費篇幅列出它的方法和獲取的物件中的屬性了，請直接參考 [model/storages.py](https://github.com/veripress/veripress/blob/master/veripress/model/storages.py) 中的 `Storage` 類和 [model/models.py](https://github.com/veripress/veripress/blob/master/veripress/model/models.py) 中的類定義。

**鑒於獲取頁面部件需要使用 `storage` 物件，如果你沒有精力或興趣查看源碼，可以直接參考預設主題的 [sidebar.html](https://github.com/veripress/themes/blob/default/templates/sidebar.html) 文件。**

在上面的 `sidebar.html` 中你會看到一個 `{{ widget|content|safe }}` 這樣的運算式，其中 `widget` 是獲取到的頁面部件物件，後面兩個 `content`、`safe` 是「篩檢程式」，前者是 VeriPress 提供的，用於把內容的抽象物件中的原始內容直接解析成 HTML 字串，後者是 Jinja2 自帶的，用於將 HTML 代碼直接顯示而不轉義。

## 獲取特定頁面的 URL

在主題中你可能需要獲取其它某個頁面的 URL 來構造連結，可以使用 Flask 提供的 `url_for()` 函數。

對於全域或主題中的 `static` 目錄的檔，使用 `url_for('static', filename='the-filename')` 來獲取。

對於 view 模式的其它頁面，例如你在巡覽列需要提供一個歸檔頁面的連結，使用類似 `url_for('.archive', year=2017)` 的調用。注意 `.archive` 以點號開頭，或者也可以使用 `view.archive`。`url_for()` 的其它參數是用來指定 view 函數的參數的，要熟練使用的話，你可能需要對 Flask 的 URL route 規則有一定瞭解，然後參考 [view/\_\_init\_\_.py](https://github.com/veripress/veripress/blob/master/veripress/view/__init__.py) 檔最底部的 URL 規則。

## 調試主題

製作主題時可能會出現異常（Exception），如果直接顯示「500 Internal Error」可能沒什麼幫助，這時可以使用 `veripress preview --debug` 來預覽，`--debug` 選項將開啟 Flask 的調試模式，在拋出異常時會將異常資訊顯示在頁面上。

## 製作主題時遇到問題？

不得不承認這篇關於如何製作主題的文檔寫的非常簡陋，如果你在自己製作過程中遇到不太明確的事情，在這裡也找不到的話，首先可以參考官方主題，如果還有疑問（或者對官方主題的寫法不太認同），請毫不吝嗇地提交 [issue](https://github.com/veripress/veripress/issues/new)。

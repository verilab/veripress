---
title: 主題
author: Richard Chien
created: 2017-03-20
updated: 2017-03-20
---

VeriPress 原生支援主題切換，通過設定檔的 `THEME` 配置項來指定要使用的主題，內部通過這個配置項，來渲染相應主題目錄中的範本檔。與此同時，`veripress` 命令還提供了方便的主題管理系列子命令。

## 安裝官方主題

目前官方主題有 default、clean-doc 等，可以在 [veripress/themes](https://github.com/veripress/themes) 查看最新的官方主題清單和預覽（或截圖）。

要安裝官方主題，使用如下命令：

```sh
$ veripress theme install theme-name  # theme-name 換成要安裝的主題名稱
```

這個命令會使用 Git 將 [veripress/themes](https://github.com/veripress/themes) 倉庫中與指定的主題名同名的分支克隆到本地的 `themes` 目錄，並預設使用同樣的名字作為本地的主題名稱。例如，上面給出的命令將把 [veripress/themes](https://github.com/veripress/themes) 的 theme-name 分支克隆到本地的 `themes/theme-name` 目錄。

如果你想在本地使用不同的主題名，比如把官方的 clean-doc 安裝為本地的 doc 主題，那麼可以使用 `--name` 參數來指定，如：

```sh
$ veripress theme install clean-doc --name doc
```

這將會把 clean-doc 主題安裝到 `themes/doc` 目錄，從而你可以把設定檔的 `THEME` 設置為 `doc` 來使用它，而不是 `clean-doc`。

## 安裝協力廠商主題

`veripress theme install` 命令同樣可以用來安裝 GitHub 上的協力廠商主題，例如你想安裝的主題在 someone/the-theme 倉庫（的 master 分支），則可以使用下面命令來安裝它：

```sh
$ veripress theme install someone/the-theme
```

不加參數的情況下，會把 master 分支克隆到 `themes`，並以 `the-theme` 作為本地主題名稱。你可以通過 `--branch` 和 `--name` 參數指定分支和名稱：

```sh
$ veripress theme install someone/the-theme --branch the-branch --name theme-name
```

上面命令會把 someone/the-theme 倉庫的 the-branch 分支克隆到 `themes/theme-name` 目錄，從而可以將 `THEME` 設置為 `theme-name` 來使用它。

## 更新和刪除主題

下面兩條命令分別可以更新和刪除已安裝的主題：

```sh
$ veripress theme update theme-name
$ veripress theme uninstall theme-name
```

前者相當於執行了 `git pull`，後者相當於刪除了 `themes` 目錄中的相應主題子目錄。

另外，已經安裝的所有主題可以通過 `veripress theme list` 列出。

## 在已有主題的基礎上自訂

由於主題是一個通用化的東西，可能你在使用的時候需要進行個性化的簡單定制，例如修改巡覽列、使用自訂佈局等。

通常，主題的作者在製作主題時，會允許使用者將自己的範本檔放在主題目錄的 `custom` 子目錄中，來覆蓋主題本身的同名範本檔，而不影響該主題原先的代碼，從而不影響後期的主題更新。此外，VeriPress 在渲染範本檔時，也會優先使用 `custom` 子目錄中的同名範本檔。

下面先給出兩種使用場景，關於範本檔具體如何編寫，請參考 [製作主題](making-your-own-theme.html) 和 Jinja2 範本引擎的 [設計文檔](http://jinja.pocoo.org/docs/2.9/templates/)。

### 修改主題範本的某一部分

主題的範本檔中通常使用類似 `include` 的語句來引入每個小部分，以 default 主題為例，它的 `layout.html` 範本中有一行：

```
{% include ['custom/navbar.html', 'navbar.html'] ignore missing %}
```

這行會優先引入 `custom` 中的 `navbar.html`，如果不存在，則使用主題自帶的。因此你可以在 `custom` 中創建自訂的 `navbar.html`，來添加你需要的巡覽列項。

### 在文章或頁面中使用自訂佈局

還記得文章和頁面的 YAML 頭部的 `layout` 項嗎，默認分別為 `post` 和 `page`，對應主題的 `post.html` 和 `page.html` 範本檔。如果你需要自訂，則可以在主題的 `custom` 目錄中創建新的佈局的範本檔。

例如你需要一個新的名叫 `simple-page` 的佈局，就新建範本檔 `custom/simple-page.html`，假設內容如下：

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

此時你就可以在自訂頁面中指定 `layout` 為 `simple-page`，從而使用上面的範本來顯示這個頁面，如：

```
---
title: 一個簡單頁面
layout: simple-page
---

這是一個非常簡單的頁面。
```

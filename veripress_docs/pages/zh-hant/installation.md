---
title: 安裝
author: Richard Chien
created: 2017-03-19
updated: 2017-03-20
---

要使用 VeriPress，你的電腦上需要安裝有 Python 3.4 或更新版本和 pip 命令。如果你的系統中同時安裝有 Python 2.x 版本，你可能需要將下面的 `python` 和 `pip` 命令換成 `python3` 和 `pip3`，此外對於非 root 或非管理員使用者，還需要加 `sudo` 或使用管理員身份啟動命令列。

## 系統全域安裝

使用 pip 命令即可從 PyPI 上安裝最新的 release 版本：

```sh
$ pip install veripress
```

安裝之後一個 `veripress` 命令會被安裝在系統中，通常在 `/usr/local/bin/veripress`。在命令列中運行 `veripress --help` 可以查看命令的使用幫助，當然，如果這是你第一次使用，你可能更需要首先閱讀後面的 [開始使用](getting-started.html) 文檔。

## 在 virtualenv 中安裝

由於安裝 VeriPress 的同時會安裝一些依賴包，你可能不希望這些依賴裝到系統的全域環境，這種情況下，使用 virtualenv 創建一個虛擬環境是一種不錯的選擇。

如果你還沒有安裝 virtualenv，請使用下面命令安裝：

```sh
$ pip install virtualenv
```

然後到一個適當的目錄，運行下列命令：

```sh
$ mkdir my-veripress
$ cd my-veripress
$ virtualenv venv
```

這將會在 `venv` 資料夾中創建一個虛擬環境，要使用這個虛擬環境，運行如下：

```sh
$ source venv/bin/activate  # Linux or macOS
$ venv\Scripts\activate  # Windows
```

然後安裝 VeriPress：

```sh
$ pip install veripress
```

要退出虛擬環境，運行：

```sh
$ deactivate
```

在 virtualenv 中使用可以獲得一個隔離的環境，但同時也需要多餘的命令來進入和離開虛擬環境，因此你需要根據情況選擇適合自己的安裝方式。

## 在 Windows 上安裝

在 Windows 上安裝 VeriPress 沒有什麼特殊要求，只要正確安裝了 Python 和 pip，就可以正常使用 `pip install veripress` 來安裝，同樣你也可以使用 virtualenv。

但由於 Windows 的特殊性，如果你在安裝和之後的使用過程中遇到了問題，請提交 issue 回饋。

此外，後面的文檔中給出的示例命令將會統一使用 Unix 命令，一般在 Windows 上都有相對應的命令可以完成同樣的操作（比如創建資料夾）。

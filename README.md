# FFXIV Patcher Python

這是一個用於處理《Final Fantasy XIV》(FFXIV) 遊戲資料的 Python 工具。此工具可以匯出遊戲中的文字資料，並支援將 SeString 格式轉換為可讀的文字。

## 功能特色

- 支援從遊戲檔案中匯出文字資料
- 支援多種語言匯出（日文、英文、德文、法文、簡體中文、繁體中文、韓文）
- 可將 SeString bytecode 直接轉為 hexcode
- 可將 SeString bytecode 轉為符合 python 語法的 f-string 以利後續透過 evaluate expression 的方式轉換為 hexcode

## 環境需求

- Python 3.12

## 設定說明

在 `config/.env` 檔案中可以設定以下選項：

### 基本設定
- `language`: 選擇匯出語言
  - 可選值："Japanese", "English", "German", "French", "ChineseSimplified", "ChineseTraditional", "Korean"

### 路徑設定
- `folder_path`: 遊戲檔案路徑
  - 可以直接指定包含 `0a0000.win32*` 檔案的資料夾
- `target_path`: 匯出目標路徑

### 匯出選項
- `ONLY_STR_MODE`: 是否僅匯出字串資料
- `HEX_STR_MODE`: 是否將 SeString 直接匯出為 hexcode

### evaluate設定
- `evaluate_folder_path`: evaluate 來源資料夾路徑
  - 預設值："./resources/output/2025.04.16.0000.0000"
- `evaluate_target_path`: evaluate 結果輸出路徑
  - 預設值："./resources/evaluate_output/"

## 使用方式

### 1. 匯出遊戲資料

執行以下指令匯出遊戲資料：

```bash
python main.py
```

這將會：
- 讀取指定資料夾中的遊戲檔案
- 解析並匯出文字資料
- 將結果儲存到目標資料夾中

### 2. evaluate SeString 資料

執行以下指令評估匯出的資料：

```bash
python evaluate_main.py
```

這將會：
- 讀取資料夾中的 CSV 檔案
- 透過 python f-string 將 SeString macro evaluate 成 SeString hexcode

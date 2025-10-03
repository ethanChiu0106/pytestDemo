# Pytest API 自動化測試框架

## 簡介

基於 Pytest 的自動化測試框架，專為驗證後端服務的 **WebSocket API** 和 **Restful API** 而設計。

## 專案目的

此框架主要處理 API 自動化測試覆蓋。它解決了以下核心問題：

*   **WebSocket API 測試**：利用 `asyncio` 和 `websockets` 庫處理非同步通訊，並實作了智能化的請求-回應匹配機制，能夠精準篩選預期回應，有效避免非預期訊息（如廣播通知）的干擾。
*   **Restful API 測試**：透過 `requests` 庫，提供 Restful API 請求發送與回應驗證能力。
*   **報告可讀性**：整合 Allure Report，生成豐富且易於分析的測試報告，幫助快速定位問題。
*   **模組化與可維護性**：採用模組化設計，將 API 請求、測試數據和測試案例分離，便於擴展和維護。
*   **集中式設定管理**：透過 `secrets.yml` 統一管理不同環境的設定與密鑰，提高安全性與配置彈性。

## 主要功能

*   **非同步 WebSocket 測試**：支援 `async/await` 語法，高效處理 WebSocket 連線和訊息交換。
*   **Restful API 測試**：使用 `requests` 庫，提供直觀的 HTTP 請求發送和回應處理。
*   **Allure 報告整合**：自動生成詳細的測試執行報告，包含步驟、截圖（如果適用）和環境信息。
*   **動態數據驅動**：測試資料由 test_data 目錄下的 Python 產生器動態生成。
*   **模組化 API 封裝**：將複雜的 API 請求邏輯封裝在獨立的類別中，簡化測試案例編寫。
*   **環境特定設定**：透過命令列參數切換不同的測試環境（如 QA, Dev）。

## 使用工具

*   **語言**：Python 3.11+
*   **測試框架**：Pytest
*   **環境與套件管理**：uv
*   **WebSocket 客戶端**：websockets
*   **Restful API 客戶端**：requests
*   **數據序列化**：msgpack
*   **數據壓縮**：gzip
*   **測試報告**：Allure Report
*   **Python 版本管理**：pyenv (可選)

## 安裝與設定

### 先決條件

*   Git
*   Python 3.11+
*   uv
*   Allure (用於生成報告)

### 步驟

1.  **克隆專案**：
    ```bash
    git clone <your-repository-url>
    cd pytest-demo
    ```

2.  **設定 Python 版本 (可選, 如使用 pyenv)**：
    ```bash
    pyenv install 3.11.9
    pyenv local 3.11.9
    ```

3.  **建立虛擬環境並同步依賴 (使用 uv)**：
    ```bash
    # 使用 uv 建立虛擬環境 (預設會建立在 .venv 資料夾)
    uv venv

    # 啟用虛擬環境 (Windows)
    .\.venv\Scripts\activate

    # 根據 uv.lock 同步依賴
    uv sync
    ```

4.  **設定密鑰與環境變數**：
    ```bash
    # 複製模板檔案
    cp config/secrets.yml.template config/secrets.yml
    ```
    接著，請開啟 `config/secrets.yml` 並填入您環境所需的設定值與帳號密碼。此檔案已被 `.gitignore` 忽略，不會被提交到版本庫中。


## 使用方式

### 執行測試

此專案使用 `--env` 參數來指定要執行的測試環境。您可以根據是否已啟用虛擬環境，選擇以下任一方式執行：

*   **方式一：已啟用虛擬環境**
    (需先執行 `.\.venv\Scripts\activate`)
    ```bash
    pytest [其他參數...]
    ```

*   **方式二：未啟用虛擬環境**
    ```bash
    uv run pytest [其他參數...]
    ```

**範例：**

*   **執行 QA 環境的所有測試**：
    ```bash
    # 方式一
    pytest --env qa

    # 方式二
    uv run pytest --env qa
    ```

*   **僅執行標記為 'scenario' 的情境測試**：
    ```bash
    # 方式一
    pytest --env qa -m scenario

    # 方式二
    uv run pytest --env qa -m scenario
    ```
*註：兩種方式都會因為 `pytest.ini` 的設定而自動產生 Allure 測試結果。*

### 生成並查看 Allure 報告

在執行測試並生成 `allure-results` 後：

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### 配置檔案

*   `config/secrets.yml`: 核心設定檔，用於存放所有環境的 URL、帳號密碼及其他敏感資訊。**此檔案不應被提交到 Git**。
*   `config/secrets.yml.template`: `secrets.yml` 的模板檔案，定義了設定檔應有的結構。
*   `test_data/*.yml`: 存放非敏感的、用於數據驅動的測試資料。

## 專案結構

```
pytest-demo/
├── api/                # 封裝 WebSocket 和 Restful API 請求和回應邏輯
├── config/             # 環境設定檔 (secrets.yml, secrets.yml.template)
├── scripts/            # 工具腳本
├── testcases/          # 測試案例 (按模組劃分)
├── test_data/          # 測試案例所需的資料模型與生成邏輯
├── utils/              # 工具函數和基礎類
├── allure-results/     # Allure 測試結果輸出目錄
├── allure-report/      # 生成的 Allure 報告目錄
├── conftest.py         # Pytest fixture 和 hook 函數
├── pytest.ini          # Pytest 配置
├── pyproject.toml      # 專案依賴與建置設定
├── uv.lock             # 鎖定的依賴版本檔案
└── .gitignore          # Git 忽略文件配置
```

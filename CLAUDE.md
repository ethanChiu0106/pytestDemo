# CLAUDE.md

pytest + Playwright + Allure 的自動化測試專案，涵蓋 HTTP API、WebSocket 與 Web UI。

---

## 執行方式

本專案以 **uv** 管理，不要直接呼叫 `.venv\Scripts\python.exe`。

```bash
uv run pytest
```

```bash
uvx ruff@0.13.2 check .
```

API 測試需要後端服務，先啟動 mock-server（位於本 repo 之外的 `../mock-server`）：

```bash
cd ../mock-server && uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

UI 測試打的是公開的 SauceDemo，不需額外服務。環境以 `--env` 切換（`qa` / `dev`），設定在 `config/secrets.yml`；`dev` 目前沒有 `urls.ui`，跑 UI 測試需用 `qa`。

---

## 程式碼慣例

- **Docstring 用 Google 風格**（`Args:` / `Returns:` / `Raises:`），所有公開的函式、類別、模組都要有。首行以動詞開頭、結尾不加句點。完整範例見 `.gemini/gemini.md`。
- **測試資料與測試邏輯分離**，資料放 `test_data/`。
- **優先使用 `conftest.py` 既有的 fixture**；需要新的通用前置條件時才新增。
- **Commit 遵循 Conventional Commits**：type 為 `feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore`，主旨用祈使句、50 字元內、結尾不加句號。

`testcases/` 依協定分 `api_test/`（`http` / `ws` / `scenario`）與 `ui_test/`，`test_data/` 的結構與之對應。

---

## 授權機制（API 測試最常用）

三個 fixture 的分工是**身分**：

| 需求 | fixture |
|---|---|
| 測登入／註冊本身（**不該**帶 token） | `auth_api`（匿名 `AuthAPI`） |
| 呼叫需要授權的 API | `authed_api`（已認證的 Provider） |
| token 字串本身 | `access_token` |
| 匿名的其他 API，或流程中自行切換身分 | `api_provider`（匿名 Provider） |

```python
def test_get_item(self, authed_api: ApiClientProvider, case: GetItemCase):
    item_api = authed_api.get(ItemAPI)
```

宣告 `authed_api` 就會自動先登入。要換使用者用 indirect parametrize：
`@pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)`。

**認證資訊存放在 client 自身的 `default_headers`，絕不要寫進 `requests.Session`**——session 是 package 範圍共用的，寫進去會污染其他測試。多身分並存用 `api_provider.with_auth(token)`，它回傳新的 Provider，不影響原本的。

新增 API class 時**不需修改 conftest**，但必須宣告 `service`（存 enum 本身，不是 `.value`）：

```python
class OrderAPI(BaseRequest):
    service = Service.FRONT
```

---

## 會靜默失敗的四個坑

**1. `--clean-alluredir` 在 pytest 啟動時就清空結果。**
`pytest.ini` 的 `addopts` 含此參數，所以任何收集到 0 個測試的執行（`--collect-only`、篩選無結果、collection 失敗）都會清光上次的結果。之後 `allure generate` 不會報錯，只會產生一份 `total: 0` 的空報告。

**2. Allure 的 title / description 必須在 call 階段套用。**
由根 `conftest.py` 的 `pytest_runtest_call` hook 處理。**搬進 fixture 會完全無效且沒有任何錯誤訊息**——測試照樣全綠，只有報告名稱悄悄退回 `test_login[login_success]`。`allure.title` 也不能當 `pytest.param` 的 mark（不是 MarkDecorator）。
已知限制：setup 階段失敗時沒有 title，這是 `allure.dynamic` 的先天限制，非缺陷。

**3. package scope 的範圍是「定義該 fixture 的 conftest 所在套件」，涵蓋所有子目錄。**
`testcases/api_test/conftest.py` 的 package fixture 涵蓋 `http/`、`ws/`、`scenario/` 全部。
另外：若 conftest 所在目錄**沒有 `__init__.py`**，package scope 會靜默退化成 session scope。

**4. Allure 報告退化不會讓測試變紅。**
動到 `create_param_from_case`、conftest hook 或 case 資料模型時，只看測試綠燈不足以驗證。需檢查 `allure-results/*.json` 的 `name`、`description` 與 labels，並特別確認 **async 測試**（ws / scenario）。

---

## 測試資料的約定

`expected` 的形狀依消費者而不同，**不要試圖統一**：

- **API 單步驟**：`{'result': ..., 'schema': ...}`（型別 `Expectation`，`schema` 選填）
- **API 情境**：`{步驟名: Expectation}`
- **UI**：自有結構，且**不經過 `verify_case_auto`**（UI 是流程中多點斷言，沒有單一回應可比對）

`ResultBase` 把 HTTP 的 `status_code` 與 body 壓平在同一層，所以 `expected` 裡的 `code` 與 `status_code` 其實來自不同層級。這點已評估過，結論是**維持現狀**——壓平雖然概念上不乾淨，但用起來方便，拆開屬於行為變更，風險大於可讀性收益。

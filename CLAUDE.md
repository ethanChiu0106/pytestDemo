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

**Allure CLI 的版本以 `.github/workflows/tests.yml` 的 `ALLURE_VERSION` 為準**，本機要跟它一致。版本不一致時報告版面會跟 GitHub Pages 不同，且沒有任何錯誤提示。用 `allure --version` 確認，scoop 使用者執行 `scoop update allure`。

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

**案例一律用 `CaseBuilder` 建立**（`test_data/common/case_builder.py`）。每檔開頭建一個 builder 固定住分類欄位，之後每個案例只需 `id` / `title` / `request` / `expected` 四項：

```python
get_item = CaseBuilder(
    GetItemCase,
    epic='物品相關功能',
    feature='獲取物品',
    story_base='獲取物品',
    marks=[PytestMark.SINGLE],
)

get_item.negative(id='get_item_not_found', title='獲取不存在的物品', request=..., expected=...)
```

`positive()` / `negative()` 會自動掛上對應的 mark 並推導 `story`（`'{正/反}向情境 - {story_base}'`）。需要更細的分組時（例如「邊界值情境」，或同一檔的反向要拆成帳號錯誤／密碼錯誤）再顯式傳 `story`。`description` 與 `severity` 皆選填。

每檔的 `XxxCase` 是**型別別名**（`XxxCase = TestCaseData[XxxRequest]`），不是新類別——分類欄位都在 builder 上，別名只負責綁定型別讓測試簽名好讀。不需要請求參數的 API（如取得列表）連 `XxxRequest` 都不用建，別名寫成 `XxxCase = TestCaseData`、案例傳 `request=None` 即可。

`TestCaseData` 有**兩個**型別參數：`TestCaseData[請求型別, 預期型別]`。第二個的預設值是 `Expectation`（API 單步驟的形狀），所以 API 單步驟的別名只寫一個參數即可。其他形狀要顯式指定，見下方〈`expected` 的形狀〉。

**只手填 Allure 的 Behaviors 階層（`epic` / `feature` / `story`）。** Suites（`parentSuite` / `suite` / `subSuite`）由 allure-pytest 依模組與類別名自動推導，已驗證三層都會填滿，**不要再加回 `parent_suite` / `suite` / `sub_suite` 欄位**——兩套階層描述同一批測試，手動維護兩份只會不同步。

**唯一不套 builder 的是 API 情境測試**（`test_data/api_test_data/scenario/user_profile_scenario.py`），它直接呼叫 `case_builder.py` 的 `create_param_from_case()`；理由寫在該檔註解裡——只有單一案例，攤提常數的價值不成立，且它的 marks 只有層級標籤、沒有正/反向之分。它的 `UserProfileScenarioCase` 因此是繼承 `TestCaseData` 的 dataclass（`epic` / `feature` 為欄位預設值），而非上面說的型別別名。

**判準是「案例數」，不是「在不在 `scenario/` 目錄」。** UI 情境測試（`test_data/ui_test_data/scenario/purchase.py`）同樣只有一個案例，但它**有**套 builder，寫法是 `ui_purchase.positive(...)`、`marks=[PytestMark.SCENARIO]`。兩支的差異純粹是先後寫成、未統一，不是刻意的設計區分——動到任一支時照該檔現有寫法走，不要拿另一支當範本。

---

`expected` 的形狀依消費者而不同，**不要試圖統一**。四種形狀各有型別，由 `TestCaseData` 的第二個型別參數綁定，全部定義在 `test_data/common/base.py`：

| 場景 | 型別 | 別名寫法 |
|---|---|---|
| API 單步驟 | `Expectation`（`result` 必填、`schema` 選填） | `TestCaseData[XxxRequest]`（預設值，免寫） |
| API 情境 | `dict[str, Expectation]`，以步驟名為鍵 | `TestCaseData[XxxRequest, dict[str, Expectation]]` |
| UI 登入類 | `UILoginExpectation` | `TestCaseData[XxxRequest, UILoginExpectation]` |
| UI 流程類 | `UIPurchaseExpectation` | `TestCaseData[XxxRequest, UIPurchaseExpectation]` |

UI **不經過 `verify_case_auto`**（UI 是流程中多點斷言，沒有單一回應可比對）。把 UI 形狀的 `expected` 傳進 API 的 builder 或 `verify_case_auto`，型別檢查會擋下來，不必等到執行期。

型別參數的預設值用到 PEP 696，Python 3.13 前需要 `typing-extensions`，已列入依賴。

`ResultBase` 把 HTTP 的 `status_code` 與 body 壓平在同一層，所以 `expected` 裡的 `code` 與 `status_code` 其實來自不同層級。這點已評估過，結論是**維持現狀**——壓平雖然概念上不乾淨，但用起來方便，拆開屬於行為變更，風險大於可讀性收益。

---

## 預期結果與頁面常數放哪裡

`test_data/common/expectations.py` 存的是 `Expectation` 的**零件**，不是完整的 `Expectation`：

```python
expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Auth.Schemas.LOGIN_SUCCESS}
#                   └─ 填進 result 的值      └─ 填進 schema 的結構
```

`Schemas` 底下一律是 schema，其餘是 result 的值。schema 用 `_http_schema(data)` / `_ws_schema(data)` 建立，回應外框固定、只有 `data` 依 API 而不同。

放哪裡依「這是什麼東西」決定，不看引用次數：

| 種類 | 位置 |
|---|---|
| 錯誤碼、回應 schema | `expectations.py`，即使只用一次。這是被測系統的契約 |
| 頁面網址 regex、選擇器 | 各 Page Object 的類別屬性，例如 `CheckoutPage.STEP_ONE_URL_REGEX` |
| 只有單一資料檔用得到的預期值 | 該資料檔內，例如 `purchase.py` 的 `details` |

**不要在 `expectations.py` 放 URL regex。** 那是頁面位置，消費者是測試檔，放這裡會逼測試為了一個網址去 import `test_data`。

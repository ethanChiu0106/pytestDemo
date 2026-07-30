from dataclasses import dataclass
from typing import Generic, List, Optional

from typing_extensions import NotRequired, TypedDict, TypeVar

from .enums import AllureSeverity, PytestMark


class Expectation(TypedDict):
    """單一次 API 回應的預期結果，供 `verify_case_auto` 使用。

    - result: 預期的欄位值，只比對此處列出的鍵
    - schema: 預期的巢狀結構與型別 (選填)
    """

    result: dict
    schema: NotRequired[dict]


class UILoginExpectation(TypedDict):
    """UI 登入案例的預期結果。

    UI 測試不經過 `verify_case_auto`，斷言散在流程各處，因此形狀由測試本身決定。
    """

    success: bool
    error_message: Optional[str]


class UIPurchaseDetails(TypedDict):
    """UI 購買流程在結帳總覽與完成頁需要逐項比對的文字。"""

    quantity: str
    product_name: str
    payment_info: str
    shipping_info: str
    item_total: str
    tax: str
    final_total: str
    complete_header: str
    complete_text: str


class UIPurchaseExpectation(TypedDict):
    """UI 購買流程案例的預期結果。"""

    details: UIPurchaseDetails


# 代表請求結構的泛型型別變數
RequestType = TypeVar('RequestType')

# 代表預期結果結構的泛型型別變數。
# 預設為 `Expectation` (API 單步驟測試的形狀)，因此單步驟的型別別名只需指定請求型別。
ExpectedType = TypeVar('ExpectedType', default=Expectation)


@dataclass
class TestCaseData(Generic[RequestType, ExpectedType]):
    """一個測試案例的完整定義：測試資料本身，加上 Allure 報告用的分類標籤。

    分類標籤之所以放在案例上而非測試函式上，是因為這些測試都是 data-driven 的——
    同一個測試函式會跑出多個案例，每個案例在報告中需要各自的標題與階層。

    `expected` 的形狀依消費者而不同，由第二個型別參數綁定，刻意不統一：

    - API 單步驟: `Expectation` (預設值，別名只需寫 `TestCaseData[XxxRequest]`)
    - API 情境: `dict[str, Expectation]`，以步驟名為鍵
    - UI: 各測試自有的形狀，如 `UILoginExpectation`、`UIPurchaseExpectation`

    只手動填 Allure 的 Behaviors 階層 (epic / feature / story)。Suites 階層
    (parentSuite / suite) 由 allure-pytest 依測試所在的模組自動推導，不需要也
    不應該再手填一次——兩套階層填的是同一批測試，重複維護只會不同步。
    """

    # --- 沒有預設值的欄位必須在前面 ---
    title: str
    story: str
    request: Optional[RequestType]
    expected: ExpectedType
    marks: List[PytestMark]
    epic: str
    feature: str

    # --- 有預設值的欄位必須在後面 ---
    severity: AllureSeverity = AllureSeverity.NORMAL
    description: str = ''

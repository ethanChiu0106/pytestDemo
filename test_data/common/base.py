from dataclasses import dataclass
from typing import Generic, List, Optional, TypedDict, TypeVar

from .enums import AllureSeverity, PytestMark

# 代表請求結構的泛型型別變數
RequestType = TypeVar('RequestType')


class Expectation(TypedDict, total=False):
    """單一次 API 回應的預期結果，供 `verify_case_auto` 使用。

    - result: 預期的欄位值，只比對此處列出的鍵
    - schema: 預期的巢狀結構與型別

    情境測試的 expected 是 `dict[str, Expectation]` (以步驟名為鍵)；
    UI 測試不經過 `verify_case_auto`，有自己的預期結構。
    """

    result: dict
    schema: dict


@dataclass
class TestCaseData(Generic[RequestType]):
    """一個測試案例的完整定義：測試資料本身，加上 Allure 報告用的分類標籤。

    分類標籤之所以放在案例上而非測試函式上，是因為這些測試都是 data-driven 的——
    同一個測試函式會跑出多個案例，每個案例在報告中需要各自的標題與階層。

    只手動填 Allure 的 Behaviors 階層 (epic / feature / story)。Suites 階層
    (parentSuite / suite) 由 allure-pytest 依測試所在的模組自動推導，不需要也
    不應該再手填一次——兩套階層填的是同一批測試，重複維護只會不同步。
    """

    # --- 沒有預設值的欄位必須在前面 ---
    title: str
    story: str
    request: Optional[RequestType]
    expected: dict
    marks: List[PytestMark]
    epic: str
    feature: str

    # --- 有預設值的欄位必須在後面 ---
    severity: AllureSeverity = AllureSeverity.NORMAL
    description: str = ''

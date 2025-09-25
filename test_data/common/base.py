from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Protocol, TypeVar


from .enums import AllureSeverity, PytestMark

# 代表請求結構的泛型型別變數
RequestType = TypeVar('RequestType')


@dataclass
class TestCaseData(Generic[RequestType]):
    """測試案例的核心資料 (請求、預期結果等)"""

    request: Optional[RequestType]
    expected: Dict[str, Any]
    marks: List[PytestMark]


@dataclass
class AllureCase:
    """基礎測試案例，包含用於 Allure 報告的分類標籤"""

    # 沒有預設值的欄位必須在前面
    title: str
    description: str
    sub_suite: str
    story: str
    parent_suite: str
    suite: str
    epic: str
    feature: str

    # 有預設值的欄位必須在後面
    severity: AllureSeverity = AllureSeverity.NORMAL  # 使用自訂的 Enum


class CombinedTestCase(Protocol[RequestType]):
    """
    一個 Protocol，定義了 create_param_from_case 所期望的組合介面。
    它明確列出了來自 TestCaseData 和 AllureCase 的所有屬性，以提供精確的型別提示。
    """

    # 來自 TestCaseData 的屬性
    request: Optional[RequestType]
    expected: Dict[str, Any]
    marks: List[PytestMark]

    # 來自 AllureCase 的屬性
    title: str
    description: str
    parent_suite: str
    suite: str
    sub_suite: str
    epic: str
    feature: str
    story: str
    severity: AllureSeverity

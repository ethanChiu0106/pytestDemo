"""提供測試案例的建構器，收斂各測試資料檔重複的分類欄位"""

from typing import Generic, List, Type, TypeVar

import pytest

from .base import TestCaseData
from .enums import AllureSeverity, PytestMark
from .helpers import create_param_from_case

CaseType = TypeVar('CaseType', bound=TestCaseData)


class CaseBuilder(Generic[CaseType]):
    """為單一功能的測試資料檔固定住分類欄位，逐案例只需描述測試意圖

    正/反向的 mark 與 `story` 都由 `positive` / `negative` 推導，因此不可能出現
    「案例是反向情境，marks 卻掛 POSITIVE」這種錯誤——那種錯誤不會讓測試變紅，
    只會讓 `pytest -m negative` 悄悄漏掉案例。

    每個案例必填的只有 `id`、`title`、`request`、`expected` 四項。

    用法:

        update_name = CaseBuilder(
            UpdateNameCase,
            epic='使用者相關功能',
            feature='更新名稱功能',
            story_base='變更名稱',
            marks=[PytestMark.SINGLE, PytestMark.WS],
        )

        update_name.negative(id='...', title='...', request=..., expected=...)
    """

    def __init__(
        self,
        case_cls: Type[CaseType],
        *,
        epic: str,
        feature: str,
        story_base: str,
        marks: List[PytestMark],
    ):
        """初始化建構器

        Args:
            case_cls: 要建立的測試案例 dataclass。
            epic: Allure Behaviors 階層的最上層。
            feature: Allure Behaviors 階層的中間層。
            story_base: story 的基底，正向推導為 '正向情境 - {story_base}'、
                反向為 '反向情境 - {story_base}'。需要更細的分組時，個別案例
                可傳入 `story` 覆寫。
            marks: 此資料檔所有案例共通的 mark (協定與測試層級)，正/反向不必列入。
        """
        self._case_cls = case_cls
        self._epic = epic
        self._feature = feature
        self._story_base = story_base
        self._marks = marks

    def positive(
        self,
        *,
        id: str,
        title: str,
        request,
        expected,
        story: str = None,
        description: str = '',
        severity: AllureSeverity = AllureSeverity.NORMAL,
    ) -> pytest.param:
        """建立一個正向案例

        Args:
            id: 測試案例的 ID，用於報告與 `-k` 篩選。
            title: Allure 報告顯示的標題。
            request: 此案例的請求資料。
            expected: 此案例的預期結果。
            story: Allure 的 story 分類，未提供時推導為 '正向情境 - {story_base}'。
            description: Allure 報告顯示的描述，與 title 重複時可省略。
            severity: Allure 的嚴重級別，預設為 NORMAL。

        Returns:
            已掛好 pytest mark 與 Allure 標籤的 `pytest.param`。
        """
        return self._build(
            PytestMark.POSITIVE,
            '正向情境',
            id=id,
            title=title,
            request=request,
            expected=expected,
            story=story,
            description=description,
            severity=severity,
        )

    def negative(
        self,
        *,
        id: str,
        title: str,
        request,
        expected,
        story: str = None,
        description: str = '',
        severity: AllureSeverity = AllureSeverity.NORMAL,
    ) -> pytest.param:
        """建立一個反向案例

        邊界值案例也走這裡——判準是「預期失敗」，而非 story 怎麼寫。這類案例
        通常會傳入自己的 `story` (例如 '邊界值情境 - ...') 以在報告中獨立成組。

        Args:
            id: 測試案例的 ID，用於報告與 `-k` 篩選。
            title: Allure 報告顯示的標題。
            request: 此案例的請求資料。
            expected: 此案例的預期結果。
            story: Allure 的 story 分類，未提供時推導為 '反向情境 - {story_base}'。
            description: Allure 報告顯示的描述，與 title 重複時可省略。
            severity: Allure 的嚴重級別，預設為 NORMAL。

        Returns:
            已掛好 pytest mark 與 Allure 標籤的 `pytest.param`。
        """
        return self._build(
            PytestMark.NEGATIVE,
            '反向情境',
            id=id,
            title=title,
            request=request,
            expected=expected,
            story=story,
            description=description,
            severity=severity,
        )

    def _build(
        self,
        polarity_mark: PytestMark,
        story_prefix: str,
        *,
        id: str,
        title: str,
        request,
        expected,
        story: str,
        description: str,
        severity: AllureSeverity,
    ) -> pytest.param:
        """組出案例並轉為 pytest.param (供 `positive` / `negative` 共用)"""
        case = self._case_cls(
            title=title,
            story=story or f'{story_prefix} - {self._story_base}',
            request=request,
            expected=expected,
            marks=[polarity_mark, *self._marks],
            epic=self._epic,
            feature=self._feature,
            severity=severity,
            description=description,
        )
        return create_param_from_case(case, id=id)

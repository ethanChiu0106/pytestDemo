"""提供測試案例的建構器，收斂各測試資料檔重複的分類欄位"""

from typing import Generic, List, Type, TypeVar

import pytest

from .base import TestCaseData
from .enums import AllureSeverity, PytestMark
from .helpers import create_param_from_case

CaseType = TypeVar('CaseType', bound=TestCaseData)


class CaseBuilder(Generic[CaseType]):
    """為單一功能的測試資料檔固定住分類欄位，逐案例只需描述測試意圖

    `sub_suite` 與正/反向的 mark 由 `positive` / `negative` 推導，因此不可能出現
    「案例是反向情境，marks 卻掛 POSITIVE」這種錯誤——那種錯誤不會讓測試變紅，
    只會讓 `pytest -m negative` 悄悄漏掉案例。

    用法:

        update_name = CaseBuilder(UpdateNameCase, sub_suite='變更名稱',
                                marks=[PytestMark.SINGLE, PytestMark.WS])

        update_name.negative(id='...', title='...', description='...',
                            story='...', request=..., expected=...)
    """

    def __init__(self, case_cls: Type[CaseType], sub_suite: str, marks: List[PytestMark]):
        """初始化建構器

        Args:
            case_cls: 要建立的測試案例 dataclass。
            sub_suite: sub_suite 的基底，正向會補上 ' - 成功'、反向補上 ' - 失敗'。
            marks: 此資料檔所有案例共通的 mark (協定與測試層級)，正/反向不必列入。
        """
        self._case_cls = case_cls
        self._sub_suite = sub_suite
        self._marks = marks

    def positive(
        self,
        *,
        id: str,
        title: str,
        description: str,
        story: str,
        request,
        expected,
        severity: AllureSeverity = AllureSeverity.NORMAL,
    ) -> pytest.param:
        """建立一個正向案例

        Args:
            id: 測試案例的 ID，用於報告與 `-k` 篩選。
            title: Allure 報告顯示的標題。
            description: Allure 報告顯示的描述。
            story: Allure 的 story 分類。
            request: 此案例的請求資料。
            expected: 此案例的預期結果。
            severity: Allure 的嚴重級別，預設為 NORMAL。

        Returns:
            已掛好 pytest mark 與 Allure 標籤的 `pytest.param`。
        """
        return self._build(
            PytestMark.POSITIVE,
            '成功',
            id=id,
            title=title,
            description=description,
            story=story,
            request=request,
            expected=expected,
            severity=severity,
        )

    def negative(
        self,
        *,
        id: str,
        title: str,
        description: str,
        story: str,
        request,
        expected,
        severity: AllureSeverity = AllureSeverity.NORMAL,
    ) -> pytest.param:
        """建立一個反向案例

        邊界值案例也走這裡——判準是「預期失敗」，而非 story 怎麼寫。

        Args:
            id: 測試案例的 ID，用於報告與 `-k` 篩選。
            title: Allure 報告顯示的標題。
            description: Allure 報告顯示的描述。
            story: Allure 的 story 分類。
            request: 此案例的請求資料。
            expected: 此案例的預期結果。
            severity: Allure 的嚴重級別，預設為 NORMAL。

        Returns:
            已掛好 pytest mark 與 Allure 標籤的 `pytest.param`。
        """
        return self._build(
            PytestMark.NEGATIVE,
            '失敗',
            id=id,
            title=title,
            description=description,
            story=story,
            request=request,
            expected=expected,
            severity=severity,
        )

    def _build(
        self,
        polarity_mark: PytestMark,
        sub_suite_suffix: str,
        *,
        id: str,
        title: str,
        description: str,
        story: str,
        request,
        expected,
        severity: AllureSeverity,
    ) -> pytest.param:
        """組出案例並轉為 pytest.param (供 `positive` / `negative` 共用)"""
        case = self._case_cls(
            title=title,
            description=description,
            sub_suite=f'{self._sub_suite} - {sub_suite_suffix}',
            story=story,
            request=request,
            expected=expected,
            marks=[polarity_mark, *self._marks],
            severity=severity,
        )
        return create_param_from_case(case, id=id)

"""
產生與「獲取多個物品」功能相關的測試資料。
"""

from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import HTTP

# 此 API 不需要請求參數，案例的 request 一律為 None
GetItemsCase = TestCaseData


get_items = CaseBuilder(
    GetItemsCase,
    epic='物品相關功能',
    feature='獲取多個物品',
    story_base='獲取多個物品',
    marks=[PytestMark.SINGLE, PytestMark.HTTP],
)


def generate_get_items_cases() -> list:
    """
    產生獲取多個物品 API 的測試情境。
    """
    return [
        get_items.positive(
            id='get_items_success',
            title='成功獲取所有物品列表',
            request=None,
            expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Item.Schemas.GET_ITEM_LIST},
            description='測試是否能成功獲取所有物品的列表',
        ),
    ]

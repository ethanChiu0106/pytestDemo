"""
產生與「獲取多個物品」功能相關的測試資料。
"""

from dataclasses import dataclass

from test_data.common.base import Expectation, TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import HTTP


@dataclass
class GetItemsRequest:
    """獲取多個物品 API 的請求資料 (此API不需要參數)"""

    pass


@dataclass
class GetItemsCase(TestCaseData[GetItemsRequest]):
    """獲取多個物品 API 的測試案例"""

    expected: Expectation

    parent_suite: str = 'HTTP API 測試'
    suite: str = '物品'
    epic: str = '物品相關功能'
    feature: str = '獲取多個物品'


get_items = CaseBuilder(GetItemsCase, sub_suite='獲取多個物品', marks=[PytestMark.SINGLE, PytestMark.HTTP])


def generate_get_items_cases() -> list:
    """
    產生獲取多個物品 API 的測試情境。
    """
    return [
        get_items.positive(
            id='get_items_success',
            title='成功獲取所有物品列表',
            description='測試是否能成功獲取所有物品的列表',
            story='正向情境 - 成功獲取所有物品',
            request=GetItemsRequest(),
            expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Item.Schemas.GET_ITEM_LIST},
        ),
    ]

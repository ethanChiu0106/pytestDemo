"""
產生與「物品」功能相關的測試資料。
"""

from dataclasses import dataclass

from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import HTTP


@dataclass
class GetItemRequest:
    """獲取物品 API 的請求資料"""

    item_id: int


GetItemCase = TestCaseData[GetItemRequest]


get_item = CaseBuilder(
    GetItemCase,
    epic='物品相關功能',
    feature='獲取物品',
    story_base='獲取物品',
    marks=[PytestMark.SINGLE],
)

NOT_FOUND_EXPECTED = {'result': HTTP.Item.GetItem.NOT_FOUND, 'schema': HTTP.Common.Schemas.FAIL}


def generate_get_item_cases() -> list:
    """
    產生獲取物品 API 的測試情境。
    """
    return [
        get_item.positive(
            id='get_item_success',
            title='獲取存在的物品',
            request=GetItemRequest(item_id=1),
            expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Item.Schemas.GET_SINGLE_ITEM},
            story='正向情境 - 成功獲取物品',
            description='使用 item_id=1 測試是否能成功獲取物品',
        ),
        get_item.negative(
            id='get_item_not_found',
            title='獲取不存在的物品',
            request=GetItemRequest(item_id=999999),
            expected=NOT_FOUND_EXPECTED,
            story='反向情境 - 物品不存在',
            description='使用一個極大的 item_id 測試物品不存在的情境',
        ),
        get_item.negative(
            id='get_item_with_id_zero',
            title='使用 item_id=0',
            request=GetItemRequest(item_id=0),
            expected=NOT_FOUND_EXPECTED,
            story='邊界值情境 - 無效的 item_id',
            description='使用 item_id=0 測試邊界值',
        ),
    ]

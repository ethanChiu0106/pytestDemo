"""
產生與「透過 WS 獲取所有物品」功能相關的測試資料。
"""

from api.ws_constants import ItemFlow, OpCode
from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation

# 此 API 不需要請求參數，案例的 request 一律為 None
GetItemsCase = TestCaseData


get_items_ws = CaseBuilder(
    GetItemsCase,
    epic='物品相關功能',
    feature='透過 WS 獲取物品',
    story_base='獲取所有物品',
    marks=[PytestMark.SINGLE, PytestMark.WS],
)


def generate_get_items_cases() -> list:
    """
    產生獲取所有物品的測試情境。
    """
    success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, OpCode.S2CItemFlow, ItemFlow.GetAllItems)

    return [
        get_items_ws.positive(
            id='get_all_items_ws_success',
            title='成功獲取所有物品列表',
            request=None,
            expected={'result': success_expected, 'schema': WebSocket.Schemas.ITEM_LIST},
            description='測試連線後，是否可以成功獲取所有物品的列表。',
        ),
    ]

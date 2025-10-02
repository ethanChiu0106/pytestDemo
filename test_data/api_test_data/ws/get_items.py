"""
產生與「透過 WS 獲取所有物品」功能相關的測試資料。
"""

from dataclasses import dataclass

from api.ws_constants import ItemFlow, OpCode
from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_param_from_case, create_ws_expectation


@dataclass
class GetItemsRequest:
    """獲取所有物品 API 的請求資料 (此請求為空)"""

    pass


@dataclass
class GetItemsCase(AllureCase, TestCaseData[GetItemsRequest]):
    """透過 WS 獲取所有物品的測試案例"""

    parent_suite: str = 'WebSocket 測試'
    suite: str = '獲取物品'
    epic: str = '物品相關功能'
    feature: str = '透過 WS 獲取物品'


def generate_get_items_cases() -> list:
    """
    產生獲取所有物品的測試情境。
    """
    success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, OpCode.S2CItemFlow, ItemFlow.GetAllItems)

    cases = [
        # --- 正向情境 ---
        create_param_from_case(
            GetItemsCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 獲取所有物品',
                sub_suite='獲取所有物品 - 成功',
                title='成功獲取所有物品列表',
                description='測試連線後，是否可以成功獲取所有物品的列表。',
                request=GetItemsRequest(),
                expected={
                    'result': success_expected,
                    'schema': WebSocket.Schemas.ITEM_LIST,
                },
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='get_all_items_ws_success',
        ),
    ]

    return cases

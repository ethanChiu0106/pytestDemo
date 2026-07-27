"""
產生與「物品」功能相關的 WebSocket 測試資料。
"""

from dataclasses import dataclass, field

from api.ws_constants import ItemFlow, OpCode
from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation


@dataclass
class GetItemWsRequest:
    """透過 WebSocket 獲取物品的請求資料"""

    # 使用 field(default=None) 讓 id 成為可選，以測試不提供 id 的情境
    item_id: int | None = field(default=None)


GetItemWsCase = TestCaseData[GetItemWsRequest]


op_code = OpCode.S2CItemFlow
sub_code = ItemFlow.GetItemById
success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)
fail_item_not_found = create_ws_expectation(WebSocket.Item.ITEM_NOT_FOUND, op_code, sub_code)
fail_id_not_provide = create_ws_expectation(WebSocket.Item.ITEM_ID_NOT_PROVIDED, op_code, sub_code)


get_item_ws = CaseBuilder(
    GetItemWsCase,
    epic='物品相關功能',
    feature='獲取物品 (WS)',
    story_base='獲取物品',
    marks=[PytestMark.SINGLE, PytestMark.WS],
)


def generate_get_item_ws_cases() -> list:
    """
    產生獲取物品 WebSocket API 的測試情境。
    """
    return [
        get_item_ws.positive(
            id='get_item_ws_success',
            title='獲取存在的物品',
            request=GetItemWsRequest(item_id=1),
            expected={'result': success_expected, 'schema': WebSocket.Schemas.SINGLE_ITEM},
            story='正向情境 - 成功獲取物品',
            description='使用 item_id=1 測試是否能成功獲取物品',
        ),
        get_item_ws.negative(
            id='get_item_ws_not_found',
            title='獲取不存在的物品',
            request=GetItemWsRequest(item_id=999999),
            expected={'result': fail_item_not_found, 'schema': WebSocket.Schemas.FAIL},
            story='反向情境 - 物品不存在',
            description='使用一個極大的 item_id 測試物品不存在的情境',
        ),
        get_item_ws.negative(
            id='get_item_ws_id_not_provided',
            title='請求中不帶 item_id',
            request=GetItemWsRequest(item_id=None),
            expected={'result': fail_id_not_provide, 'schema': WebSocket.Schemas.FAIL},
            story='邊界值情境 - 不提供 item_id',
            description='測試請求的 data 中不包含 item_id 欄位',
        ),
    ]

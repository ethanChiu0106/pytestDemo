"""
產生與「物品」功能相關的 WebSocket 測試資料。
"""

from dataclasses import dataclass, field

from api.ws_constants import ItemFlow, OpCode
from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_param_from_case, create_ws_expectation


@dataclass
class GetItemWsRequest:
    """透過 WebSocket 獲取物品的請求資料"""

    # 使用 field(default=None) 讓 id 成為可選，以測試不提供 id 的情境
    item_id: int | None = field(default=None)


@dataclass
class GetItemWsCase(AllureCase, TestCaseData[GetItemWsRequest]):
    """獲取物品 WebSocket API 的測試案例"""

    parent_suite: str = 'WebSocket 測試'
    suite: str = '物品'
    epic: str = '物品相關功能'
    feature: str = '獲取物品 (WS)'


op_code = OpCode.S2CItemFlow
sub_code = ItemFlow.GetItemById
success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)
fail_item_not_found = create_ws_expectation(WebSocket.Item.ITEM_NOT_FOUND, op_code, sub_code)
fail_id_not_provide = create_ws_expectation(WebSocket.Item.ITEM_ID_NOT_PROVIDED, op_code, sub_code)


def generate_get_item_ws_cases() -> list:
    """
    產生獲取物品 WebSocket API 的測試情境。
    """
    cases = [
        create_param_from_case(
            GetItemWsCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 成功獲取物品',
                sub_suite='獲取物品 (WS) - 成功',
                title='獲取存在的物品',
                description='使用 item_id=1 測試是否能成功獲取物品',
                request=GetItemWsRequest(item_id=1),
                expected={'result': success_expected, 'schema': WebSocket.Schemas.SINGLE_ITEM},
                marks=[PytestMark.POSITIVE, PytestMark.WS, PytestMark.SINGLE],
            ),
            id='get_item_ws_success',
        ),
        create_param_from_case(
            GetItemWsCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 物品不存在',
                sub_suite='獲取物品 (WS) - 失敗',
                title='獲取不存在的物品',
                description='使用一個極大的 item_id 測試物品不存在的情境',
                request=GetItemWsRequest(item_id=999999),
                expected={'result': fail_item_not_found, 'schema': WebSocket.Schemas.FAIL},
                marks=[PytestMark.NEGATIVE, PytestMark.WS, PytestMark.SINGLE],
            ),
            id='get_item_ws_not_found',
        ),
        create_param_from_case(
            GetItemWsCase(
                severity=AllureSeverity.NORMAL,
                story='邊界值情境 - 不提供 item_id',
                sub_suite='獲取物品 (WS) - 失敗',
                title='請求中不帶 item_id',
                description='測試請求的 data 中不包含 item_id 欄位',
                request=GetItemWsRequest(item_id=None),
                expected={'result': fail_id_not_provide, 'schema': WebSocket.Schemas.FAIL},
                marks=[PytestMark.NEGATIVE, PytestMark.WS, PytestMark.SINGLE],
            ),
            id='get_item_ws_id_not_provided',
        ),
    ]
    return cases

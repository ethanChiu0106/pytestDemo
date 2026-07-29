"""
產生與「取得使用者資訊」功能相關的測試資料。
"""

from api.ws_constants import OpCode, PlayerFlow
from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation

# 此 API 不需要請求參數，案例的 request 一律為 None
GetUserInfoCase = TestCaseData


op_code = OpCode.S2CPlayerFlow
sub_code = PlayerFlow.GetPlayerInfo
success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)


get_user_info = CaseBuilder(
    GetUserInfoCase,
    epic='使用者相關功能',
    feature='取得使用者資訊功能',
    story_base='取得使用者資訊',
    marks=[PytestMark.SINGLE],
)


def generate_get_user_info_cases() -> list:
    """
    產生取得使用者資訊 API 的測試情境。
    """
    return [
        get_user_info.positive(
            id='get_user_info_success',
            title='取得使用者資訊成功',
            request=None,
            expected={'result': success_expected, 'schema': WebSocket.Schemas.PLAYER_INFO},
            description='測試登入後，是否可以成功取得使用者自己的資訊',
        ),
    ]

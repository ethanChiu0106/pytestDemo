"""
產生與「取得使用者資訊」功能相關的測試資料。
"""

from dataclasses import dataclass

from api.ws_constants import OpCode, PlayerFlow
from test_data.common.base import Expectation, TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation


@dataclass
class GetUserInfoRequest:
    """取得使用者資訊 API 的請求資料 (此 API 無須參數)"""

    pass


@dataclass
class GetUserInfoCase(TestCaseData[GetUserInfoRequest]):
    """取得使用者資訊 WS 的測試案例"""

    expected: Expectation

    parent_suite: str = 'WebSocket 測試'
    suite: str = '取得使用者資訊'
    epic: str = '使用者相關功能'
    feature: str = '取得使用者資訊功能'


op_code = OpCode.S2CPlayerFlow
sub_code = PlayerFlow.GetPlayerInfo
success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)


get_user_info = CaseBuilder(GetUserInfoCase, sub_suite='取得使用者資訊', marks=[PytestMark.SINGLE, PytestMark.WS])


def generate_get_user_info_cases() -> list:
    """
    產生取得使用者資訊 API 的測試情境。
    """
    return [
        get_user_info.positive(
            id='get_user_info_success',
            title='取得使用者資訊成功',
            description='測試登入後，是否可以成功取得使用者自己的資訊',
            story='正向情境 - 使用者成功取得資訊',
            request=GetUserInfoRequest(),
            expected={'result': success_expected, 'schema': WebSocket.Schemas.PLAYER_INFO},
        ),
    ]

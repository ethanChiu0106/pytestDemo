"""
產生與「更新名稱」功能相關的測試資料。
"""

from dataclasses import dataclass

from api.ws_constants import OpCode, PlayerFlow
from test_data.common.base import Expectation, TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation


@dataclass
class UpdateNameRequest:
    """更新名稱 API 的請求資料"""

    name: str


@dataclass
class UpdateNameCase(TestCaseData[UpdateNameRequest]):
    """更新名稱 WS 的測試案例"""

    expected: Expectation

    parent_suite: str = 'WebSocket 測試'
    suite: str = '變更名稱'
    epic: str = '使用者相關功能'
    feature: str = '更新名稱功能'


op_code = OpCode.S2CPlayerFlow
sub_code = PlayerFlow.UpdateName
success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)
fail_invalid_format = create_ws_expectation(WebSocket.User.INVALID_USERNAME_FORMAT, op_code, sub_code)

update_name = CaseBuilder(UpdateNameCase, sub_suite='變更名稱', marks=[PytestMark.SINGLE, PytestMark.WS])

SUCCESS_EXPECTED = {'result': success_expected, 'schema': WebSocket.Schemas.PLAYER_INFO}
INVALID_FORMAT_EXPECTED = {'result': fail_invalid_format, 'schema': WebSocket.Schemas.FAIL}


def generate_update_name_cases() -> list:
    """
    產生更新名稱的測試情境。
    """
    return [
        update_name.positive(
            id='update_name_success_3_chars',
            title='變更名稱成功-3碼',
            description='測試登入後, 是否可以成功使用3碼變更名稱',
            story='正向情境 - 變更名稱',
            request=UpdateNameRequest(name='測試稱'),
            expected=SUCCESS_EXPECTED,
        ),
        update_name.positive(
            id='update_name_success_4_chars',
            title='變更名稱成功-4碼',
            description='測試登入後, 是否可以成功使用4碼變更名稱',
            story='正向情境 - 變更名稱',
            request=UpdateNameRequest(name='測試名稱'),
            expected=SUCCESS_EXPECTED,
        ),
        update_name.positive(
            id='update_name_success_12_chars',
            title='變更名稱成功-12碼',
            description='測試登入後, 是否可以成功使用12碼變更名稱',
            story='正向情境 - 變更名稱',
            request=UpdateNameRequest(name='測' * 12),
            expected=SUCCESS_EXPECTED,
        ),
        update_name.negative(
            id='update_name_failure_too_short',
            title='格式錯誤 - 2碼',
            description='名稱使用 - 2碼',
            story='反向情境 - 變更名稱',
            request=UpdateNameRequest(name='測試'),
            expected=INVALID_FORMAT_EXPECTED,
        ),
        update_name.negative(
            id='update_name_failure_too_long',
            title='格式錯誤 - 13碼',
            description='名稱使用 - 13碼',
            story='反向情境 - 變更名稱',
            request=UpdateNameRequest(name='測' * 13),
            expected=INVALID_FORMAT_EXPECTED,
        ),
        update_name.negative(
            id='update_name_failure_format_wrong',
            title='格式錯誤 - 非中英數',
            description='名稱使用 - 非中英數',
            story='反向情境 - 變更名稱',
            request=UpdateNameRequest(name='=---'),
            expected=INVALID_FORMAT_EXPECTED,
        ),
    ]

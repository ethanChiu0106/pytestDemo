"""
產生與「綁定手機」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from api.ws_constants import OpCode, PlayerFlow
from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_ws_expectation
from utils.config_loader import get_config

fake = Faker('zh_TW')


@dataclass
class BindPhoneRequest:
    """綁定手機 API 的請求資料"""

    telephone: str


BindPhoneCase = TestCaseData[BindPhoneRequest]


bind_phone = CaseBuilder(
    BindPhoneCase,
    epic='使用者相關功能',
    feature='綁定手機功能',
    story_base='綁定手機',
    marks=[PytestMark.SINGLE],
)


def generate_bind_phone_cases() -> list:
    """
    產生綁定手機的測試情境。
    """
    phone_number = fake.numerify(text='09########')
    duplicate_phone = get_config().user('duplicate_phone_user').phone
    op_code = OpCode.S2CPlayerFlow
    sub_code = PlayerFlow.BindPhone
    success_expected = create_ws_expectation(WebSocket.Common.SUCCESS, op_code, sub_code)
    fail_not_provided = create_ws_expectation(WebSocket.User.TELEPHONE_NOT_PROVIDED, op_code, sub_code)
    fail_invalid_format = create_ws_expectation(WebSocket.User.INVALID_TELEPHONE_FORMAT, op_code, sub_code)
    fail_already_registered = create_ws_expectation(WebSocket.User.TELEPHONE_ALREADY_REGISTERED, op_code, sub_code)

    invalid_format_expected = {'result': fail_invalid_format, 'schema': WebSocket.Schemas.FAIL}

    return [
        bind_phone.positive(
            id='bind_phone_success',
            title='綁定成功 - 格式正確',
            request=BindPhoneRequest(telephone=phone_number),
            expected={'result': success_expected, 'schema': WebSocket.Schemas.PLAYER_INFO},
            description='測試登入後, 是否可以成功綁定手機 (09開頭, 10碼數字)',
        ),
        bind_phone.negative(
            id='bind_phone_failure_not_provided',
            title='格式錯誤 - 未提供手機號碼',
            request=BindPhoneRequest(telephone=''),
            expected={'result': fail_not_provided, 'schema': WebSocket.Schemas.FAIL},
            description='請求中未帶入手機號碼',
        ),
        bind_phone.negative(
            id='bind_phone_failure_invalid_prefix',
            title='格式錯誤 - 非09開頭',
            request=BindPhoneRequest(telephone='0812345678'),
            expected=invalid_format_expected,
            description='手機號碼開頭不是09',
        ),
        bind_phone.negative(
            id='bind_phone_failure_too_short',
            title='格式錯誤 - 長度不足 (9碼)',
            request=BindPhoneRequest(telephone='091234567'),
            expected=invalid_format_expected,
            description='手機號碼長度不足10碼',
        ),
        bind_phone.negative(
            id='bind_phone_failure_too_long',
            title='格式錯誤 - 長度過長 (11碼)',
            request=BindPhoneRequest(telephone='09123456789'),
            expected=invalid_format_expected,
            description='手機號碼長度超過10碼',
        ),
        bind_phone.negative(
            id='bind_phone_failure_contains_non_digits',
            title='格式錯誤 - 包含非數字字元',
            request=BindPhoneRequest(telephone='091234567a'),
            expected=invalid_format_expected,
            description='手機號碼包含非數字字元',
        ),
        bind_phone.negative(
            id='bind_phone_failure_already_registered',
            title='綁定失敗 - 手機號碼已被註冊',
            request=BindPhoneRequest(telephone=duplicate_phone),
            expected={'result': fail_already_registered, 'schema': WebSocket.Schemas.FAIL},
            description='嘗試綁定一個已經被其他帳號註冊的手機號碼',
        ),
    ]

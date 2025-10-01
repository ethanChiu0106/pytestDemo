"""
產生與「綁定手機」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from utils.config_loader import get_config

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import WebSocket
from test_data.common.helpers import create_param_from_case

fake = Faker('zh_TW')


@dataclass
class BindPhoneRequest:
    """綁定手機 API 的請求資料"""

    telephone: str


@dataclass
class BindPhoneCase(AllureCase, TestCaseData[BindPhoneRequest]):
    """綁定手機 WS 的測試案例"""

    parent_suite: str = 'WebSocket 測試'
    suite: str = '綁定手機'
    epic: str = '使用者相關功能'
    feature: str = '綁定手機功能'


def generate_bind_phone_cases() -> list:
    """
    產生綁定手機的測試情境。
    """
    phone_number = fake.numerify(text='09########')
    duplicate_phone = get_config().get('users', {}).get('duplicate_phone_user').get('phone')
    cases = [
        # --- 正向情境 ---
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 綁定手機',
                sub_suite='綁定手機 - 成功',
                title='綁定成功 - 格式正確',
                description='測試登入後, 是否可以成功綁定手機 (09開頭, 10碼數字)',
                request=BindPhoneRequest(telephone=phone_number),
                expected=WebSocket.SUCCESS,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_success',
        ),
        # --- 反向情境 ---
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='格式錯誤 - 未提供手機號碼',
                description='請求中未帶入手機號碼',
                request=BindPhoneRequest(telephone=''),
                expected=WebSocket.User.TELEPHONE_NOT_PROVIDED,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_not_provided',
        ),
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='格式錯誤 - 非09開頭',
                description='手機號碼開頭不是09',
                request=BindPhoneRequest(telephone='0812345678'),
                expected=WebSocket.User.INVALID_TELEPHONE_FORMAT,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_invalid_prefix',
        ),
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='格式錯誤 - 長度不足 (9碼)',
                description='手機號碼長度不足10碼',
                request=BindPhoneRequest(telephone='091234567'),
                expected=WebSocket.User.INVALID_TELEPHONE_FORMAT,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_too_short',
        ),
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='格式錯誤 - 長度過長 (11碼)',
                description='手機號碼長度超過10碼',
                request=BindPhoneRequest(telephone='09123456789'),
                expected=WebSocket.User.INVALID_TELEPHONE_FORMAT,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_too_long',
        ),
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='格式錯誤 - 包含非數字字元',
                description='手機號碼包含非數字字元',
                request=BindPhoneRequest(telephone='091234567a'),
                expected=WebSocket.User.INVALID_TELEPHONE_FORMAT,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_contains_non_digits',
        ),
        create_param_from_case(
            BindPhoneCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 綁定手機',
                sub_suite='綁定手機 - 失敗',
                title='綁定失敗 - 手機號碼已被註冊',
                description='嘗試綁定一個已經被其他帳號註冊的手機號碼',
                request=BindPhoneRequest(telephone=duplicate_phone),
                expected=WebSocket.User.TELEPHONE_ALREADY_REGISTERED,
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='bind_phone_failure_already_registered',
        ),
    ]

    return cases

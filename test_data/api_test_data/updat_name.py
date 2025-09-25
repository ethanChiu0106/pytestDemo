"""
產生與「更新名稱」功能相關的測試資料。
"""

from dataclasses import dataclass

from ..common.base import AllureCase, TestCaseData
from ..common.enums import AllureSeverity, PytestMark
from ..common.expectations import WebSocket
from ..common.helpers import create_param_from_case


@dataclass
class UpdateNameRequest:
    """更新名稱 API 的請求資料"""

    name: str


@dataclass
class UpdateNameCase(AllureCase, TestCaseData[UpdateNameRequest]):
    """更新名稱 WS 的測試案例"""

    parent_suite: str = 'WS 測試'
    suite: str = '變更名稱'
    epic: str = '使用者相關功能'
    feature: str = '更新名稱功能'


def generate_update_name_cases() -> list:
    """
    產生更新名稱的測試情境。
    """
    cases = [
        create_param_from_case(
            UpdateNameCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 變更名稱',
                sub_suite='變更名稱 - 成功',
                title='變更名稱成功',
                description='測試登入後，是否可以成功變更自己的名稱',
                request=UpdateNameRequest(name='測試名稱'),
                expected=WebSocket.SUCCESS,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='update_name_success',
        ),
        create_param_from_case(
            UpdateNameCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 變更名稱',
                sub_suite='變更名稱 - 失敗',
                title='格式錯誤 - 2碼',
                description='名稱使用 - 2碼',
                request=UpdateNameRequest(name='測試'),
                expected=WebSocket.User.INVALID_USERNAME_FORMAT,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='update_name_failure_too_short',
        ),
        create_param_from_case(
            UpdateNameCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 變更名稱',
                sub_suite='變更名稱 - 失敗',
                title='格式錯誤 - 13碼',
                description='名稱使用 - 13碼',
                request=UpdateNameRequest(name='測' * 13),
                expected=WebSocket.User.INVALID_USERNAME_FORMAT,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='update_name_failure_too_long',
        ),
        create_param_from_case(
            UpdateNameCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 變更名稱',
                sub_suite='變更名稱 - 失敗',
                title='格式錯誤 - 非中英數',
                description='名稱使用 - 非中英數',
                request=UpdateNameRequest(name='=---'),
                expected=WebSocket.User.INVALID_USERNAME_FORMAT,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='update_name_failure_format_wrong',
        ),
    ]

    return cases

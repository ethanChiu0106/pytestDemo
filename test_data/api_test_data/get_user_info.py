"""
產生與「取得使用者資訊」功能相關的測試資料。
"""

from dataclasses import dataclass

from ..common.base import AllureCase, TestCaseData
from ..common.enums import AllureSeverity, PytestMark
from ..common.expectations import WebSocket
from ..common.helpers import create_param_from_case


@dataclass
class GetUserInfoRequest:
    """取得使用者資訊 API 的請求資料 (此 API 無須參數)"""

    pass


@dataclass
class GetUserInfoCase(AllureCase, TestCaseData[GetUserInfoRequest]):
    """取得使用者資訊 WS 的測試案例"""

    parent_suite: str = 'WS 測試'
    suite: str = '取得使用者資訊'
    epic: str = '使用者相關功能'
    feature: str = '取得使用者資訊功能'


def generate_get_user_info_cases() -> list:
    """
    產生取得使用者資訊 API 的測試情境。
    """
    cases = [
        create_param_from_case(
            GetUserInfoCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 使用者成功取得資訊',
                sub_suite='取得使用者資訊 - 成功',
                title='取得使用者資訊成功',
                description='測試登入後，是否可以成功取得使用者自己的資訊',
                request=GetUserInfoRequest(),
                expected=WebSocket.SUCCESS,
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.WS],
            ),
            id='get_user_info_success',
        ),
    ]

    return cases

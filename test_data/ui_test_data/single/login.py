"""
產生與使用者「登入」功能相關的 UI 測試資料。
"""

from dataclasses import dataclass
from typing import List

import pytest

from test_data.common.base import TestCaseData, UILoginExpectation
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import UI
from utils.config_loader import get_config


@dataclass
class UILoginRequest:
    """登入 UI 的請求資料 (即表單填寫的內容)"""

    username: str
    password: str


UILoginCase = TestCaseData[UILoginRequest, UILoginExpectation]


ui_login = CaseBuilder(
    UILoginCase,
    epic='UI 使用者相關功能',
    feature='登入功能',
    story_base='登入',
    marks=[PytestMark.SINGLE],
)


def generate_ui_login_cases() -> List[pytest.param]:
    """
    產生登入 UI 的測試情境。
    包含正向與反向案例。
    """
    default_user = get_config().user('ui_default_user')
    empty_field_story = '反向情境 - 欄位留空'

    return [
        ui_login.positive(
            id='ui_login_success',
            title='UI 登入成功',
            request=UILoginRequest(username=default_user.account, password=default_user.password),
            expected=UI.Login.SUCCESS,
            story='正向情境 - 使用者成功登入',
            description='輸入正確的帳號密碼，驗證是否可以成功登入',
            severity=AllureSeverity.CRITICAL,
        ),
        ui_login.negative(
            id='ui_incorrect_password',
            title='密碼錯誤',
            request=UILoginRequest(username=default_user.account, password='wrongPass123'),
            expected=UI.Login.LOGIN_FAIL,
            story='反向情境 - 密碼錯誤',
            description='輸入正確的帳號及錯誤的密碼，驗證是否顯示錯誤訊息',
        ),
        ui_login.negative(
            id='ui_incorrect_username',
            title='帳號錯誤',
            request=UILoginRequest(username='noSuchUser', password='password'),
            expected=UI.Login.LOGIN_FAIL,
            story='反向情境 - 帳號錯誤',
            description='輸入不存在的帳號，驗證是否顯示錯誤訊息',
        ),
        ui_login.negative(
            id='ui_empty_password',
            title='密碼留空',
            request=UILoginRequest(username=default_user.account, password=''),
            expected=UI.Login.EMPTY_PASSWORD,
            story=empty_field_story,
            description='帳號已輸入，密碼留空，驗證是否顯示錯誤訊息',
        ),
        ui_login.negative(
            id='ui_empty_username',
            title='帳號留空',
            request=UILoginRequest(username='', password=default_user.password),
            expected=UI.Login.EMPTY_USERNAME,
            story=empty_field_story,
            description='帳號留空，密碼已輸入，驗證是否顯示錯誤訊息',
        ),
    ]

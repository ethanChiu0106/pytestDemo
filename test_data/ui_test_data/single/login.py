"""
產生與使用者「登入」功能相關的 UI 測試資料。
"""

from dataclasses import dataclass
from typing import List

import pytest
from faker import Faker

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import UI
from test_data.common.helpers import create_param_from_case
from utils.config_loader import get_config

# 初始化 Faker
fake = Faker('zh_TW')


@dataclass
class UILoginRequest:
    """登入 UI 的請求資料 (即表單填寫的內容)"""

    username: str
    password: str


@dataclass
class UILoginCase(AllureCase, TestCaseData[UILoginRequest]):
    """登入 UI 的測試案例"""

    parent_suite: str = 'UI 測試'
    suite: str = '登入頁面'
    epic: str = 'UI 使用者相關功能'
    feature: str = '登入功能'


def generate_ui_login_cases() -> List[pytest.param]:
    """
    產生登入 UI 的測試情境。
    包含正向與反向案例。
    """
    secrets = get_config()
    default_user = secrets['users']['ui_default_user']

    cases = [
        create_param_from_case(
            UILoginCase(
                severity=AllureSeverity.CRITICAL,
                story='正向情境 - 使用者成功登入',
                sub_suite='登入 - 成功',
                title='UI 登入成功',
                description='輸入正確的帳號密碼，驗證是否可以成功登入',
                request=UILoginRequest(
                    username=default_user['account'],
                    password=default_user['password'],
                ),
                expected=UI.Login.SUCCESS,
                marks=[PytestMark.POSITIVE, PytestMark.UI_SINGLE],
            ),
            id='ui_login_success',
        ),
        create_param_from_case(
            UILoginCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 密碼錯誤',
                sub_suite='登入 - 失敗',
                title='密碼錯誤',
                description='輸入正確的帳號及錯誤的密碼，驗證是否顯示錯誤訊息',
                request=UILoginRequest(
                    username=default_user['account'],
                    password=fake.password(),
                ),
                expected=UI.Login.LOGIN_FAIL,
                marks=[PytestMark.NEGATIVE, PytestMark.UI_SINGLE],
            ),
            id='ui_incorrect_password',
        ),
        create_param_from_case(
            UILoginCase(
                sub_suite='登入 - 失敗',
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 帳號錯誤',
                title='帳號錯誤',
                description='輸入不存在的帳號，驗證是否顯示錯誤訊息',
                request=UILoginRequest(
                    username=fake.user_name(),
                    password='password',
                ),
                expected=UI.Login.LOGIN_FAIL,
                marks=[PytestMark.NEGATIVE, PytestMark.UI_SINGLE],
            ),
            id='ui_incorrect_username',
        ),
        create_param_from_case(
            UILoginCase(
                sub_suite='登入 - 失敗',
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 欄位留空',
                title='密碼留空',
                description='帳號已輸入，密碼留空，驗證是否顯示錯誤訊息',
                request=UILoginRequest(
                    username=default_user['account'],
                    password='',
                ),
                expected=UI.Login.EMPTY_PASSWORD,
                marks=[PytestMark.NEGATIVE, PytestMark.UI_SINGLE],
            ),
            id='ui_empty_password',
        ),
        create_param_from_case(
            UILoginCase(
                sub_suite='登入 - 失敗',
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 欄位留空',
                title='帳號留空',
                description='帳號留空，密碼已輸入，驗證是否顯示錯誤訊息',
                request=UILoginRequest(
                    username='',
                    password=default_user['password'],
                ),
                expected=UI.Login.EMPTY_USERNAME,
                marks=[PytestMark.NEGATIVE, PytestMark.UI_SINGLE],
            ),
            id='ui_empty_username',
        ),
    ]

    return cases

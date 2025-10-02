"""
產生與使用者「登入」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP
from test_data.common.helpers import create_param_from_case, generate_accounts
from utils.config_loader import get_config

# 初始化 Faker
fake = Faker('zh_TW')


@dataclass
class LoginRequest:
    """登入 API 的請求資料"""

    account: str
    password: str


@dataclass
class LoginCase(AllureCase, TestCaseData[LoginRequest]):
    """登入 API 的測試案例"""

    parent_suite: str = 'HTTP API 測試'
    suite: str = '登入'
    epic: str = '使用者相關功能'
    feature: str = '登入功能'


def generate_login_cases() -> list:
    """
    產生登入 API 的測試情境。
    """
    secrets = get_config()
    default_user = secrets['users']['default_user']

    cases = [
        create_param_from_case(
            LoginCase(
                severity=AllureSeverity.CRITICAL,
                story='正向情境 - 使用者成功登入',
                sub_suite='登入 - 成功',
                title='登入成功',
                description='輸入正確的帳號密碼測試是否可以登入',
                request=LoginRequest(
                    account=default_user['account'],
                    password=default_user['password'],
                ),
                expected={
                    'result': HTTP.Common.SUCCESS,
                    'schema': HTTP.Auth.Schemas.LOGIN_SUCCESS,
                },
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='login_success',
        ),
        create_param_from_case(
            LoginCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 帳號錯誤',
                sub_suite='登入 - 失敗',
                title='帳號有誤',
                description='輸入一個不存在的隨機帳號',
                request=LoginRequest(account=generate_accounts(1)[0], password='password1'),
                expected={
                    'result': HTTP.Auth.Login.ACCOUNT_ERROR,
                    'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
                },
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='incorrect_account',
        ),
        create_param_from_case(
            LoginCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 密碼錯誤',
                sub_suite='登入 - 失敗',
                title='密碼有誤',
                description='輸入正確帳號，但隨機產生錯誤密碼',
                request=LoginRequest(account=default_user['account'], password=fake.password()),
                expected={
                    'result': HTTP.Auth.Login.PASSWORD_ERROR,
                    'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
                },
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='incorrect_password',
        ),
    ]

    return cases

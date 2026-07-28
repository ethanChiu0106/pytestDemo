"""
產生與使用者「登入」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP
from test_data.common.helpers import generate_accounts
from utils.config_loader import get_config

fake = Faker('zh_TW')


@dataclass
class LoginRequest:
    """登入 API 的請求資料"""

    account: str
    password: str


LoginCase = TestCaseData[LoginRequest]


login = CaseBuilder(
    LoginCase,
    epic='使用者相關功能',
    feature='登入功能',
    story_base='登入',
    marks=[PytestMark.SINGLE, PytestMark.HTTP],
)


def generate_login_cases() -> list:
    """
    產生登入 API 的測試情境。
    """
    default_user = get_config().user('default_user')

    return [
        login.positive(
            id='login_success',
            title='登入成功',
            request=LoginRequest(account=default_user.account, password=default_user.password),
            expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Auth.Schemas.LOGIN_SUCCESS},
            story='正向情境 - 使用者成功登入',
            description='輸入正確的帳號密碼測試是否可以登入',
            severity=AllureSeverity.CRITICAL,
        ),
        login.negative(
            id='incorrect_account',
            title='帳號有誤',
            request=LoginRequest(account=generate_accounts(1)[0], password='password1'),
            expected={'result': HTTP.Auth.Login.ACCOUNT_ERROR, 'schema': HTTP.Common.FAIL_HTTP_STRUCTURE},
            story='反向情境 - 帳號錯誤',
            description='輸入一個不存在的隨機帳號',
            severity=AllureSeverity.CRITICAL,
        ),
        login.negative(
            id='incorrect_password',
            title='密碼有誤',
            request=LoginRequest(account=default_user.account, password=fake.password()),
            expected={'result': HTTP.Auth.Login.PASSWORD_ERROR, 'schema': HTTP.Common.FAIL_HTTP_STRUCTURE},
            story='反向情境 - 密碼錯誤',
            description='輸入正確帳號，但隨機產生錯誤密碼',
            severity=AllureSeverity.CRITICAL,
        ),
    ]

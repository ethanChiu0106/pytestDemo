"""
產生與使用者「註冊」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP
from test_data.common.helpers import generate_accounts

fake = Faker('zh_TW')


@dataclass
class RegisterRequest:
    """註冊 API 的請求資料"""

    account: str
    password: str


RegisterCase = TestCaseData[RegisterRequest]


register = CaseBuilder(
    RegisterCase,
    epic='使用者相關功能',
    feature='註冊功能',
    story_base='註冊',
    marks=[PytestMark.SINGLE, PytestMark.HTTP],
)

SUCCESS_EXPECTED = {'result': HTTP.Auth.Register.SUCCESS, 'schema': HTTP.Auth.Schemas.REGISTER_SUCCESS}
REPEATED_ACCOUNT_EXPECTED = {'result': HTTP.Auth.Register.REPEATED_ACCOUNT, 'schema': HTTP.Common.FAIL_HTTP_STRUCTURE}
ACCOUNT_FORMAT_EXPECTED = {
    'result': HTTP.Auth.Validation.ACCOUNT_FORMAT_ERROR,
    'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
}
PASSWORD_FORMAT_EXPECTED = {
    'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
    'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
}


def generate_register_cases() -> list:
    """
    產生註冊 API 的所有測試情境。
    """

    # --- 資料準備 ---
    # 會真的建立帳號的案例才需要隨機值，否則第二次執行就會撞「帳號已存在」
    valid_account = generate_accounts(1)[0]
    valid_password = generate_accounts(1, min_len=7)[0]
    account_5_chars = fake.password(length=5, special_chars=False)
    account_20_chars = fake.password(length=20, special_chars=False)
    password_7_chars = fake.password(length=7, special_chars=False)
    # 密碼格式在帳號重複檢查之前就被擋下，此帳號不會被建立，故可固定
    negative_test_account = 'formatTestUser'
    password_6_chars = 'abc123'
    password_21_chars = 'abcdefghij1234567890a'
    password_all_eng = 'abcdefghij'
    password_all_num = '1234567890'

    success_story = '正向情境 - 使用者成功註冊'
    account_format_story = '反向情境 - 帳號格式錯誤'
    password_format_story = '反向情境 - 密碼格式錯誤'

    return [
        register.positive(
            id='register_success_dynamic_account',
            title='註冊成功 - 動態新帳號',
            request=RegisterRequest(account=valid_account, password=valid_password),
            expected=SUCCESS_EXPECTED,
            story=success_story,
            description='帳號5~20英數, 密碼7~20英數',
            severity=AllureSeverity.CRITICAL,
        ),
        register.positive(
            id='register_success_5_chars_account_and_7_chars_password',
            title='註冊成功 - 帳號5碼, 密碼7碼(邊界值)',
            request=RegisterRequest(account=account_5_chars, password=password_7_chars),
            expected=SUCCESS_EXPECTED,
            story=success_story,
            description='帳號5碼',
            severity=AllureSeverity.CRITICAL,
        ),
        register.positive(
            id='register_success_20_chars_account_and_20_chars_password',
            title='註冊成功 - 帳號20碼, 密碼20碼(邊界值)',
            request=RegisterRequest(account=account_20_chars, password=account_20_chars),
            expected=SUCCESS_EXPECTED,
            story=success_story,
            description='帳號20碼',
            severity=AllureSeverity.CRITICAL,
        ),
        register.negative(
            id='register_with_existing_account',
            title='已存在帳號',
            request=RegisterRequest(account=valid_account, password=valid_password),
            expected=REPEATED_ACCOUNT_EXPECTED,
            story='反向情境 - 帳號已存在',
            description='反向測試：使用已知的重複帳號',
            severity=AllureSeverity.CRITICAL,
        ),
        register.negative(
            id='account_too_long',
            title='格式錯誤 - 帳號過長',
            request=RegisterRequest(account='a' * 21, password='aa123456'),
            expected=ACCOUNT_FORMAT_EXPECTED,
            story=account_format_story,
            description='反向測試：帳號長度超過20碼',
        ),
        register.negative(
            id='account_too_short',
            title='格式錯誤 - 帳號過短',
            request=RegisterRequest(account='a' * 4, password='aa123456'),
            expected=ACCOUNT_FORMAT_EXPECTED,
            story=account_format_story,
            description='反向測試：帳號長度不足5碼',
        ),
        register.negative(
            id='password_too_short',
            title='格式錯誤 - 密碼過短',
            request=RegisterRequest(account=negative_test_account, password=password_6_chars),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='反向測試：密碼長度6碼',
        ),
        register.negative(
            id='password_too_long',
            title='格式錯誤 - 密碼過長',
            request=RegisterRequest(account=negative_test_account, password=password_21_chars),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='反向測試：密碼長度21碼',
        ),
        register.negative(
            id='password_all_english',
            title='格式錯誤 - 密碼全英',
            request=RegisterRequest(account=negative_test_account, password=password_all_eng),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='反向測試：密碼全英',
        ),
        register.negative(
            id='password_all_numeric',
            title='格式錯誤 - 密碼全數',
            request=RegisterRequest(account=negative_test_account, password=password_all_num),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='反向測試：密碼全數',
        ),
    ]

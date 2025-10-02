"""
產生與使用者「註冊」功能相關的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP
from test_data.common.helpers import create_param_from_case, generate_accounts

fake = Faker('zh_TW')


@dataclass
class RegisterRequest:
    """註冊 API 的請求資料"""

    account: str
    password: str


@dataclass
class RegisterCase(AllureCase, TestCaseData[RegisterRequest]):
    """註冊 API 的測試案例"""

    parent_suite: str = 'HTTP API 測試'
    suite: str = '註冊'
    epic: str = '使用者相關功能'
    feature: str = '註冊功能'


def generate_register_cases() -> list:
    """
    產生註冊 API 的所有測試情境。
    """

    # --- 資料準備 ---
    accounts = generate_accounts(2)
    valid_account = accounts[0]
    valid_password = generate_accounts(1, min_len=7)[0]
    negative_test_account = accounts[1]
    account_5_chars = fake.password(length=5, special_chars=False)
    account_20_chars = fake.password(length=20, special_chars=False)
    password_7_chars = fake.password(length=7, special_chars=False)
    password_6_chars = fake.password(length=6, special_chars=False)
    password_21_chars = fake.password(length=21, special_chars=False)
    password_all_eng = fake.password(length=10, special_chars=False, digits=False)
    password_all_num = fake.password(length=10, special_chars=False, upper_case=False, lower_case=False)

    # --- 測試案例資料定義 ---
    test_data_definitions = [
        # 正向情境
        {
            'id': 'register_success_dynamic_account',
            'story': '正向情境 - 使用者成功註冊',
            'sub_suite': '註冊 - 成功',
            'title': '註冊成功 - 動態新帳號',
            'description': '帳號5~20英數, 密碼7~20英數',
            'account': valid_account,
            'password': valid_password,
            'expected': {
                'result': HTTP.Auth.Register.SUCCESS,
                'schema': HTTP.Auth.Schemas.REGISTER_SUCCESS,
            },
            'severity': AllureSeverity.CRITICAL,
            'marks': [PytestMark.SINGLE, PytestMark.POSITIVE, PytestMark.HTTP],
        },
        {
            'id': 'register_success_5_chars_account_and_7_chars_password',
            'story': '正向情境 - 使用者成功註冊',
            'sub_suite': '註冊 - 成功',
            'title': '註冊成功 - 帳號5碼, 密碼7碼(邊界值)',
            'description': '帳號5碼',
            'account': account_5_chars,
            'password': password_7_chars,
            'expected': {
                'result': HTTP.Auth.Register.SUCCESS,
                'schema': HTTP.Auth.Schemas.REGISTER_SUCCESS,
            },
            'severity': AllureSeverity.CRITICAL,
            'marks': [PytestMark.SINGLE, PytestMark.POSITIVE, PytestMark.HTTP],
        },
        {
            'id': 'register_success_20_chars_account_and_20_chars_password',
            'story': '正向情境 - 使用者成功註冊',
            'sub_suite': '註冊 - 成功',
            'title': '註冊成功 - 帳號20碼, 密碼20碼(邊界值)',
            'description': '帳號20碼',
            'account': account_20_chars,
            'password': account_20_chars,
            'expected': {
                'result': HTTP.Auth.Register.SUCCESS,
                'schema': HTTP.Auth.Schemas.REGISTER_SUCCESS,
            },
            'severity': AllureSeverity.CRITICAL,
            'marks': [PytestMark.SINGLE, PytestMark.POSITIVE, PytestMark.HTTP],
        },
        # 反向情境
        {
            'id': 'register_with_existing_account',
            'story': '反向情境 - 帳號已存在',
            'sub_suite': '註冊 - 失敗',
            'title': '已存在帳號',
            'description': '反向測試：使用已知的重複帳號',
            'account': valid_account,
            'password': valid_password,
            'expected': {
                'result': HTTP.Auth.Register.REPEATED_ACCOUNT,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.CRITICAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'account_too_long',
            'story': '反向情境 - 帳號格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 帳號過長',
            'description': '反向測試：帳號長度超過20碼',
            'account': 'a' * 21,
            'password': 'aa123456',
            'expected': {
                'result': HTTP.Auth.Validation.ACCOUNT_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'account_too_short',
            'story': '反向情境 - 帳號格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 帳號過短',
            'description': '反向測試：帳號長度不足5碼',
            'account': 'a' * 4,
            'password': 'aa123456',
            'expected': {
                'result': HTTP.Auth.Validation.ACCOUNT_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'password_too_short',
            'story': '反向情境 - 密碼格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 密碼過短',
            'description': '反向測試：密碼長度6碼',
            'account': negative_test_account,
            'password': password_6_chars,
            'expected': {
                'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'password_too_long',
            'story': '反向情境 - 密碼格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 密碼過長',
            'description': '反向測試：密碼長度21碼',
            'account': negative_test_account,
            'password': password_21_chars,
            'expected': {
                'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'password_all_english',
            'story': '反向情境 - 密碼格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 密碼全英',
            'description': '反向測試：密碼全英',
            'account': negative_test_account,
            'password': password_all_eng,
            'expected': {
                'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
        {
            'id': 'password_all_numeric',
            'story': '反向情境 - 密碼格式錯誤',
            'sub_suite': '註冊 - 失敗',
            'title': '格式錯誤 - 密碼全數',
            'description': '反向測試：密碼全數',
            'account': negative_test_account,
            'password': password_all_num,
            'expected': {
                'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
                'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
            },
            'severity': AllureSeverity.NORMAL,
            'marks': [PytestMark.SINGLE, PytestMark.NEGATIVE, PytestMark.HTTP],
        },
    ]

    # --- 迴圈生成測試案例 ---
    cases = []
    for data in test_data_definitions:
        case = RegisterCase(
            severity=data['severity'],
            story=data['story'],
            sub_suite=data['sub_suite'],
            title=data['title'],
            description=data['description'],
            request=RegisterRequest(account=data['account'], password=data['password']),
            expected=data['expected'],
            marks=data['marks'],
        )
        cases.append(create_param_from_case(case, id=data['id']))

    return cases

"""
產生與忘記密碼功能相關的測試資料。

"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import Auth, Common
from test_data.common.helpers import create_param_from_case
from utils.config_loader import get_config

# 初始化 Faker
fake = Faker('zh_TW')


@dataclass
class ChangePasswordRequest:
    """發送變更密碼 API 的請求資料"""

    old_password: str
    new_password: str


@dataclass
class ChangePasswordCase(AllureCase, TestCaseData[ChangePasswordRequest]):
    """變更密碼 API 的測試案例"""

    parent_suite: str = 'HTTP API 測試'
    suite: str = '變更密碼'
    epic: str = '變更密碼'
    feature: str = '變更密碼測試'


def generate_change_password_cases() -> list:
    """
    產生變更密碼 API 的測試情境。
    """
    secrets = get_config()
    # 指定此測試案例使用 change_password_user 的資料
    target_user = secrets['users']['change_password_user']
    old = target_user['password']
    new = fake.password(length=10, special_chars=False)
    password_6_chars = fake.password(length=6, special_chars=False)
    password_21_chars = fake.password(length=21, special_chars=False)
    password_all_eng = fake.password(length=10, special_chars=False, digits=False)
    password_all_num = fake.password(length=10, special_chars=False, upper_case=False, lower_case=False)

    cases = [
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.CRITICAL,
                story='正向情境 - 變更密碼成功',
                sub_suite='變更密碼 - 成功',
                title='變更密碼成功',
                description='輸入正確格式的舊密碼新密碼',
                request=ChangePasswordRequest(
                    old_password=old,
                    new_password=new,
                ),
                expected={
                    'result': Common.SUCCESS,
                    'schema': {'status_code': None, 'code': None, 'data': None},
                },
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_success',
        ),
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 舊密錯誤',
                sub_suite='變更密碼 - 失敗',
                title='變更密碼失敗-舊密碼輸入錯誤',
                description='舊密碼輸入錯誤',
                request=ChangePasswordRequest(old_password=new, new_password=new),
                expected={'result': Auth.Login.PASSWORD_ERROR, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_failure_old_password_wrong',
        ),
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 密碼格式錯誤',
                sub_suite='變更密碼 - 失敗',
                title='格式錯誤 - 密碼過短-邊界值(6碼)',
                description='密碼輸入6碼英數',
                request=ChangePasswordRequest(
                    old_password=old,
                    new_password=password_6_chars,
                ),
                expected={'result': Auth.Validation.PASSWORD_FORMAT_ERROR, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_failure_password_too_short',
        ),
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 密碼格式錯誤',
                sub_suite='變更密碼 - 失敗',
                title='格式錯誤 - 密碼過長-邊界值(21碼)',
                description='密碼輸入21碼英數',
                request=ChangePasswordRequest(
                    old_password=old,
                    new_password=password_21_chars,
                ),
                expected={'result': Auth.Validation.PASSWORD_FORMAT_ERROR, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_failure_password_too_long',
        ),
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 密碼格式錯誤',
                sub_suite='變更密碼 - 失敗',
                title='格式錯誤 - 密碼全英',
                description='密碼輸入全英',
                request=ChangePasswordRequest(
                    old_password=old,
                    new_password=password_all_eng,
                ),
                expected={'result': Auth.Validation.PASSWORD_FORMAT_ERROR, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_failure_password_all_english',
        ),
        create_param_from_case(
            ChangePasswordCase(
                severity=AllureSeverity.CRITICAL,
                story='反向情境 - 密碼格式錯誤',
                sub_suite='變更密碼 - 失敗',
                title='格式錯誤 - 密碼全數',
                description='密碼輸入全數',
                request=ChangePasswordRequest(
                    old_password=old,
                    new_password=password_all_num,
                ),
                expected={'result': Auth.Validation.PASSWORD_FORMAT_ERROR, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='change_password_failure_password_all_number',
        ),
    ]

    return cases

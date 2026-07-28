"""
產生與忘記密碼功能相關的測試資料。

"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import TestCaseData
from test_data.common.case_builder import CaseBuilder
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP
from utils.config_loader import get_config

fake = Faker('zh_TW')


@dataclass
class ChangePasswordRequest:
    """發送變更密碼 API 的請求資料"""

    old_password: str
    new_password: str


ChangePasswordCase = TestCaseData[ChangePasswordRequest]


change_password = CaseBuilder(
    ChangePasswordCase,
    epic='變更密碼',
    feature='變更密碼測試',
    story_base='變更密碼',
    marks=[PytestMark.SINGLE, PytestMark.HTTP],
)

PASSWORD_FORMAT_EXPECTED = {
    'result': HTTP.Auth.Validation.PASSWORD_FORMAT_ERROR,
    'schema': HTTP.Common.FAIL_HTTP_STRUCTURE,
}


def generate_change_password_cases() -> list:
    """
    產生變更密碼 API 的測試情境。
    """
    target_user = get_config().user('change_password_user')
    old = target_user.password
    new = fake.password(length=10, special_chars=False)
    password_6_chars = fake.password(length=6, special_chars=False)
    password_21_chars = fake.password(length=21, special_chars=False)
    password_all_eng = fake.password(length=10, special_chars=False, digits=False)
    password_all_num = fake.password(length=10, special_chars=False, upper_case=False, lower_case=False)

    password_format_story = '反向情境 - 密碼格式錯誤'

    return [
        change_password.positive(
            id='change_password_success',
            title='變更密碼成功',
            request=ChangePasswordRequest(old_password=old, new_password=new),
            expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Common.Schemas.SUCCESS_WITH_NULL_DATA},
            description='輸入正確格式的舊密碼新密碼',
            severity=AllureSeverity.CRITICAL,
        ),
        change_password.negative(
            id='change_password_failure_old_password_wrong',
            title='變更密碼失敗-舊密碼輸入錯誤',
            request=ChangePasswordRequest(old_password=new, new_password=new),
            expected={'result': HTTP.Auth.Login.PASSWORD_ERROR, 'schema': HTTP.Common.FAIL_HTTP_STRUCTURE},
            story='反向情境 - 舊密錯誤',
            description='舊密碼輸入錯誤',
        ),
        change_password.negative(
            id='change_password_failure_password_too_short',
            title='格式錯誤 - 密碼過短-邊界值(6碼)',
            request=ChangePasswordRequest(old_password=old, new_password=password_6_chars),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='密碼輸入6碼英數',
            severity=AllureSeverity.CRITICAL,
        ),
        change_password.negative(
            id='change_password_failure_password_too_long',
            title='格式錯誤 - 密碼過長-邊界值(21碼)',
            request=ChangePasswordRequest(old_password=old, new_password=password_21_chars),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='密碼輸入21碼英數',
            severity=AllureSeverity.CRITICAL,
        ),
        change_password.negative(
            id='change_password_failure_password_all_english',
            title='格式錯誤 - 密碼全英',
            request=ChangePasswordRequest(old_password=old, new_password=password_all_eng),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='密碼輸入全英',
            severity=AllureSeverity.CRITICAL,
        ),
        change_password.negative(
            id='change_password_failure_password_all_number',
            title='格式錯誤 - 密碼全數',
            request=ChangePasswordRequest(old_password=old, new_password=password_all_num),
            expected=PASSWORD_FORMAT_EXPECTED,
            story=password_format_story,
            description='密碼輸入全數',
            severity=AllureSeverity.CRITICAL,
        ),
    ]

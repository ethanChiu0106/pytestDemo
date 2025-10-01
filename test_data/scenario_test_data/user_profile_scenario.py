"""
產生使用者個人資料完整流程（註冊 -> 登入 -> 更改名稱 -> 更改密碼 -> 還原密碼）的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import Auth, Common, WebSocket
from test_data.common.helpers import create_param_from_case, generate_accounts

fake = Faker('zh_TW')


@dataclass
class UserProfileScenarioRequest:
    """使用者個人資料場景測試的請求資料集合"""

    # 註冊與登入
    account: str
    initial_password: str

    # 更新名稱
    new_name: str

    # 變更密碼
    new_password: str


@dataclass
class UserProfileScenarioCase(AllureCase, TestCaseData[UserProfileScenarioRequest]):
    """使用者個人資料場景的測試案例"""

    parent_suite: str = '情境測試'
    suite: str = '使用者個人資料'
    epic: str = '使用者個人資料完整流程'
    feature: str = '從註冊到變更資料'


def generate_user_profile_scenario_cases() -> list:
    """
    產生使用者個人資料場景的測試案例。
    """
    # --- 資料準備 ---
    account = generate_accounts(1)[0]
    initial_password = fake.password(length=10, special_chars=False)
    new_name = fake.name()
    new_password = fake.password(length=10, special_chars=False)

    # --- 測試案例定義 ---
    case_definition = {
        'id': 'user_profile_full_scenario',
        'story': '使用者個人資料完整流程',
        'sub_suite': '完整流程',
        'title': '從註冊到變更密碼的完整使用者流程',
        'description': '依序測試 1.註冊 -> 2.登入 -> 3.驗證初始資料 -> 4.變更名稱後驗證名稱 -> 5.變更密碼 -> 6.驗證新密碼 -> 7.還原密碼',
        'request_data': UserProfileScenarioRequest(
            account=account,
            initial_password=initial_password,
            new_name=new_name,
            new_password=new_password,
        ),
        'expected': {
            'register': Auth.Register.SUCCESS,
            'login': Common.SUCCESS,
            'get_initial_info': WebSocket.SUCCESS,
            'update_name': WebSocket.SUCCESS,
            'change_password': Common.SUCCESS,
            'revert_password': Common.SUCCESS,
        },
        'severity': AllureSeverity.CRITICAL,
        'marks': [PytestMark.SCENARIO],
    }

    # --- 建立測試案例 ---
    case = UserProfileScenarioCase(
        severity=case_definition['severity'],
        story=case_definition['story'],
        sub_suite=case_definition['sub_suite'],
        title=case_definition['title'],
        description=case_definition['description'],
        request=case_definition['request_data'],
        expected=case_definition['expected'],
        marks=case_definition['marks'],
    )

    return [create_param_from_case(case, id=case_definition['id'])]

"""
產生使用者個人資料完整流程（註冊 -> 登入 -> 更改名稱 -> 更改密碼 -> 還原密碼）的測試資料。
"""

from dataclasses import dataclass

from faker import Faker

from test_data.common.base import TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import HTTP, WebSocket
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
class UserProfileScenarioCase(TestCaseData[UserProfileScenarioRequest]):
    """使用者個人資料場景的測試案例"""

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

    # --- 建立測試案例 ---
    # 情境測試只有單一案例，不套用 CaseBuilder——builder 的價值是把每檔的固定
    # 欄位攤提到多個案例上，一個案例攤不到；且情境測試的 marks 只有層級標籤，
    # 沒有正/反向之分。
    case = UserProfileScenarioCase(
        severity=AllureSeverity.CRITICAL,
        story='使用者個人資料完整流程',
        title='從註冊到變更密碼的完整使用者流程',
        description=(
            '依序測試 1.註冊 -> 2.登入 -> 3.驗證初始資料 -> 4.變更名稱後驗證名稱 -> '
            '5.變更密碼 -> 6.驗證新密碼 -> 7.還原密碼'
        ),
        request=UserProfileScenarioRequest(
            account=account,
            initial_password=initial_password,
            new_name=new_name,
            new_password=new_password,
        ),
        expected={
            'register': {
                'result': HTTP.Auth.Register.SUCCESS,
                'schema': HTTP.Auth.Schemas.REGISTER_SUCCESS,
            },
            'login': {'result': HTTP.Common.SUCCESS, 'schema': HTTP.Auth.Schemas.LOGIN_SUCCESS},
            'get_initial_info': {
                'result': WebSocket.Common.SUCCESS,
                'schema': WebSocket.Schemas.PLAYER_INFO,
            },
            'update_name': {
                'result': WebSocket.Common.SUCCESS,
                'schema': WebSocket.Schemas.PLAYER_INFO,
            },
            'change_password': {
                'result': HTTP.Common.SUCCESS,
                'schema': HTTP.Common.Schemas.SUCCESS_WITH_NULL_DATA,
            },
            'revert_password': {
                'result': HTTP.Common.SUCCESS,
                'schema': HTTP.Common.Schemas.SUCCESS_WITH_NULL_DATA,
            },
        },
        marks=[PytestMark.SCENARIO],
    )

    return [create_param_from_case(case, id='user_profile_full_scenario')]

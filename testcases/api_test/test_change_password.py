import pytest

from api.auth import AuthAPI
from test_data.api_test_data.change_password import ChangePasswordCase, generate_change_password_cases
from utils import case_verify_tool as verify
from utils.allure_utils import allure_from_case
from utils.config_loader import get_config


@pytest.fixture
def password_change_session(pre_login: AuthAPI, request):
    """
    1. 透過 pre_login fixture 確保使用者已登入。
    2. 提供已登入的 API client 給測試使用。
    3. 在測試結束後，如果密碼被成功修改，則將其還原。
    """
    # pre_login 已經執行完畢，使用者已登入
    yield pre_login  # 將登入後的 AuthAPI client 提供給測試

    # --- Teardown --- #
    case: ChangePasswordCase = request.node.callspec.params.get('case')
    if case and 'change_password_success' in request.node.callspec.id:
        # 從 request 中找出是哪個 user key 被用於 pre_login
        user_key = request.node.callspec.params.get('pre_login', 'default_user')
        secrets = get_config()
        original_password = secrets['users'][user_key]['password']
        new_password = case.request.new_password

        print(f'[Teardown] 變更密碼 ({new_password}) 回原始密碼 ({original_password})')
        # pre_login 就是已登入的 AuthAPI client
        result = pre_login.change_password(new_password, original_password)
        assert result.get('code') == 0, 'Teardown 變更密碼失敗'


@pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)
@pytest.mark.parametrize('case', generate_change_password_cases())
class TestChangePassword:
    @allure_from_case
    def test_change_password(
        self, password_change_session: AuthAPI, case: ChangePasswordCase, setup_change_password_user
    ):
        auth_api = password_change_session
        request = case.request
        excepted = case.expected
        old = request.old_password
        new = request.new_password
        actual_result = auth_api.change_password(old, new)
        verify.assert_result(actual_result, excepted)

import pytest

from api.auth import AuthAPI
from test_data.api_test_data.http.change_password import ChangePasswordCase, generate_change_password_cases
from utils.api_provider import ApiClientProvider
from utils.case_verify_tool import verify_case_auto
from utils.config_loader import get_config


@pytest.fixture
def password_change_session(authed_api: ApiClientProvider, request):
    """
    1. 透過 authed_api fixture 確保使用者已登入。
    2. 提供已認證的 AuthAPI client 給測試使用。
    3. 在測試結束後，如果密碼被成功修改，則將其還原。
    """
    auth_api = authed_api.get(AuthAPI)
    yield auth_api

    # --- Teardown --- #
    case: ChangePasswordCase = request.node.callspec.params.get('case')
    if case and 'change_password_success' in request.node.callspec.id:
        # 從 request 中找出是哪個 user key 被用於前置登入
        user_key = request.node.callspec.params.get('user_data', 'default_user')
        original_password = get_config().user(user_key).password
        new_password = case.request.new_password

        print(f'[Teardown] 變更密碼 ({new_password}) 回原始密碼 ({original_password})')
        result = auth_api.change_password(new_password, original_password)
        assert result.get('code') == 0, 'Teardown 變更密碼失敗'


@pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)
@pytest.mark.parametrize('case', generate_change_password_cases())
class TestChangePassword:
    def test_change_password(
        self, password_change_session: AuthAPI, case: ChangePasswordCase, setup_change_password_user
    ):
        auth_api = password_change_session
        request = case.request
        expected = case.expected
        old = request.old_password
        new = request.new_password
        actual_result = auth_api.change_password(old, new)
        verify_case_auto(actual_result, expected)

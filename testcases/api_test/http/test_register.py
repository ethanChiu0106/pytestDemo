import pytest

from api.auth import AuthAPI
from test_data.api_test_data.http.register import RegisterCase, generate_register_cases
from test_data.common.expectations import HTTP
from utils.case_verify_tool import verify_case_auto


@pytest.fixture
def seed_existing_account(case: RegisterCase, auth_api: AuthAPI):
    """為「帳號已存在」案例預先註冊帳號，使它不必依賴「註冊成功」案例先跑過

    Args:
        case: 當前的註冊測試案例。
        auth_api: 匿名的 AuthAPI client，註冊本身不需授權。
    """
    if case.expected['result'] != HTTP.Auth.Register.REPEATED_ACCOUNT:
        return
    auth_api.register(case.request.account, case.request.password)


class TestRegister:
    @pytest.mark.parametrize('case', generate_register_cases())
    @pytest.mark.usefixtures('seed_existing_account')
    def test_register(self, case: RegisterCase, auth_api: AuthAPI):
        request = case.request
        expected = case.expected
        account = request.account
        password = request.password
        actual_result = auth_api.register(account, password)
        verify_case_auto(actual_result, expected)

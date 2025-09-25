import pytest

from api.auth import AuthAPI
from test_data.api_test_data.login import LoginCase, generate_login_cases
from utils.allure_utils import allure_from_case
from utils.case_verify_tool import assert_result


@pytest.mark.parametrize('case', generate_login_cases())
class TestLogin:
    @allure_from_case
    def test_login(self, case: LoginCase, auth_api: AuthAPI):
        request = case.request
        excepted = case.expected
        account = request.account
        password = request.password
        actual_result = auth_api.login(account, password)
        assert_result(actual_result, excepted)

import pytest

from api.user import UserAPI
from test_data.api_test_data.login import LoginCase, generate_login_cases
from utils import case_verify_tool as verify
from utils.allure_utils import allure_from_case


@pytest.mark.parametrize('case', generate_login_cases())
class TestLogin:
    @allure_from_case
    def test_login(self, case: LoginCase, user_api: UserAPI):
        request = case.request
        excepted = case.expected
        account = request.account
        password = request.password
        actual_result = user_api.login(account, password)
        verify.assert_result(actual_result, excepted)

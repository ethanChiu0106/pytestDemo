import pytest

from api.user import UserAPI
from utils.allure_utils import allure_from_case
from utils import case_verify_tool as verify
from test_data.api_test_data.register import RegisterCase, generate_register_cases


class TestRegister:
    @allure_from_case
    @pytest.mark.parametrize('case', generate_register_cases())
    def test_register(self, case: RegisterCase, user_api: UserAPI):
        request = case.request
        excepted = case.expected
        account = request.account
        password = request.password
        actual_result = user_api.register(account, password)
        verify.assert_result(actual_result, excepted)

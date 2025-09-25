import pytest

from api.auth import AuthAPI
from utils.allure_utils import allure_from_case
from utils.case_verify_tool import assert_result
from test_data.api_test_data.register import RegisterCase, generate_register_cases


class TestRegister:
    @allure_from_case
    @pytest.mark.parametrize('case', generate_register_cases())
    def test_register(self, case: RegisterCase, auth_api: AuthAPI):
        request = case.request
        excepted = case.expected
        account = request.account
        password = request.password
        actual_result = auth_api.register(account, password)
        assert_result(actual_result, excepted)

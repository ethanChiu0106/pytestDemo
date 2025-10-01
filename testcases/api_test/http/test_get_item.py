import pytest

from api.auth import AuthAPI
from api.item import Item
from test_data.api_test_data.http.get_item import GetItemCase, generate_get_item_cases
from utils.allure_utils import allure_from_case
from utils.api_provider import ApiClientProvider
from utils.case_verify_tool import verify_case_auto


@pytest.mark.parametrize('case', generate_get_item_cases())
class TestGetItem:
    @allure_from_case
    def test_get_item(self, pre_login: AuthAPI, case: GetItemCase, api_provider: ApiClientProvider):
        item_api = api_provider.get(Item)
        request = case.request
        excepted = case.expected
        item_id = request.item_id
        actual_result = item_api.get_item(item_id)
        verify_case_auto(actual_result, excepted)

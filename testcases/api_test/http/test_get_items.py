import pytest

from api.auth import AuthAPI
from api.item import Item
from test_data.api_test_data.http.get_items import GetItemsCase, generate_get_items_cases
from utils.allure_utils import allure_from_case
from utils.api_provider import ApiClientProvider
from utils.case_verify_tool import verify_case_auto


@pytest.mark.parametrize('case', generate_get_items_cases())
class TestGetItems:
    @allure_from_case
    def test_get_items(self, pre_login: AuthAPI, case: GetItemsCase, api_provider: ApiClientProvider):
        item_api = api_provider.get(Item)
        excepted = case.expected
        actual_result = item_api.get_items()
        verify_case_auto(actual_result, excepted)

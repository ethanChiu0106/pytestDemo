import pytest

from api.item import ItemWS
from test_data.api_test_data.ws.get_item import GetItemWsCase, generate_get_item_ws_cases
from test_data.api_test_data.ws.get_items import GetItemsCase, generate_get_items_cases
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import verify_case_auto


class TestItemWS:
    @allure_from_case
    @pytest.mark.parametrize('case', generate_get_item_ws_cases())
    @pytest.mark.asyncio
    async def test_get_item_ws(self, ws_connect: AsyncBaseWS, case: GetItemWsCase):
        item_ws_api = ItemWS(ws_connect)
        item_id = case.request.item_id
        expected = case.expected

        actual_result = await item_ws_api.get_item_by_id(item_id)
        verify_case_auto(actual_result, expected)

    @allure_from_case
    @pytest.mark.parametrize('case', generate_get_items_cases())
    @pytest.mark.asyncio
    async def test_get_items_ws(self, ws_connect: AsyncBaseWS, case: GetItemsCase):
        item_ws_api = ItemWS(ws_connect)
        expected = case.expected

        actual_result = await item_ws_api.get_all_items()
        verify_case_auto(actual_result, expected)

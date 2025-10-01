import pytest

from api.item import ItemWs
from test_data.api_test_data.ws.get_item import GetItemWsCase, generate_get_item_ws_cases
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import assert_result


@pytest.mark.parametrize('case', generate_get_item_ws_cases())
class TestGetItemWs:
    @allure_from_case
    @pytest.mark.asyncio
    async def test_get_item_ws(self, ws_connect: AsyncBaseWS, case: GetItemWsCase):
        item_ws_api = ItemWs(ws_connect)
        item_id = case.request.item_id
        excepted = case.expected

        actual_result = await item_ws_api.get_item_by_id(item_id)
        assert_result(actual_result, excepted)

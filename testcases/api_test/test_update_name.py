import pytest

from api.player import Player
from test_data.api_test_data.updat_name import UpdateNameCase, generate_update_name_cases
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import assert_result


class TestUpdateName:
    @allure_from_case
    @pytest.mark.asyncio
    @pytest.mark.parametrize('case', generate_update_name_cases())
    async def test_update_name(self, ws_connect: AsyncBaseWS, case: UpdateNameCase):
        player = Player(ws_connect)
        new_name = case.request.name
        excepted = case.expected
        actual_result = await player.update_name(new_name)
        assert_result(actual_result, excepted)

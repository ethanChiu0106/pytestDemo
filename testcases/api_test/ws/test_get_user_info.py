import pytest

from api.player import PlayerWS
from test_data.api_test_data.ws.get_user_info import GetUserInfoCase, generate_get_user_info_cases
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import verify_case_auto


@pytest.mark.parametrize('case', generate_get_user_info_cases())
class TestGetUserInfo:
    @allure_from_case
    @pytest.mark.asyncio
    async def test_get_user_info(self, ws_connect: AsyncBaseWS, case: GetUserInfoCase):
        player = PlayerWS(ws_connect)
        player_info = ws_connect.player_init_info
        actual_result = await player.get_player_info()
        assert player_info == actual_result.get('data'), '取得使用者資訊與實際不符'
        verify_case_auto(actual_result, case.expected)

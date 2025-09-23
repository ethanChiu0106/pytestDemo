import pytest

from api.player import Player
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS


class TestUpdateName:
    @allure_from_case
    @pytest.mark.asyncio
    async def test_update_name(self, ws_connect: AsyncBaseWS):
        player = Player(ws_connect)
        actual_result = await player.update_name('test')

import asyncio
import logging

import pytest
from api.player import Player
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS


class TestGetUserInfo:
    @allure_from_case
    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)
    async def test_get_user_info(self, ws_connect: AsyncBaseWS):
        player = Player(ws_connect)
        actual_result = await player.get_player_info()

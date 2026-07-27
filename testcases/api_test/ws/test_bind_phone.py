from typing import Callable

import allure
import pytest
import pytest_asyncio

from api.auth import AuthAPI
from api.player import PlayerWS
from test_data.api_test_data.ws.bind_phone import BindPhoneCase, generate_bind_phone_cases
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import verify_case_auto
from utils.config_loader import get_config


@pytest_asyncio.fixture(scope='module', autouse=True)
async def pre_bound_phone_user(user_creator: Callable[[str], None], auth_api: AuthAPI) -> str:
    """讓 duplicate_phone_user 綁定固定號碼，使「號碼已被註冊」的情境成立

    綁定會寫入伺服器的資料庫，斷線不會解綁，因此送出後即可關閉連線，
    不需要把連線持有到 module 結束。重綁同一使用者自己的號碼不會失敗，
    所以本 fixture 重跑多次也安全。

    Returns:
        已被綁定的手機號碼。
    """
    user_creator('duplicate_phone_user')
    user = get_config().user('duplicate_phone_user')

    with allure.step(f'前置步驟 => 使用 {user.account} 登入並綁定手機 {user.phone}'):
        result = auth_api.login(user.account, user.password)
        async with AsyncBaseWS(auth_api.ws_url_from(result)) as ws:
            await PlayerWS(ws).bind_phone(user.phone)

    return user.phone


class TestBindPhone:
    @pytest.mark.asyncio
    @pytest.mark.parametrize('case', generate_bind_phone_cases())
    async def test_bind_phone(self, ws_connect: AsyncBaseWS, case: BindPhoneCase):
        player = PlayerWS(ws_connect)
        phone = case.request.telephone
        expected = case.expected
        actual_result = await player.bind_phone(phone)
        verify_case_auto(actual_result, expected)

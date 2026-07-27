from typing import AsyncIterator

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
async def pre_bound_phone_user(setup_duplicate_phone_user: None, auth_api: AuthAPI) -> AsyncIterator[str]:
    """
    確保一個使用者已綁定一個固定的手機號碼。
    :return: 已綁定的固定手機號碼字串。
    """
    user = get_config().user('duplicate_phone_user')
    account, password, pre_bound_phone = user.account, user.password, user.phone

    with allure.step(f'前置步驟 => 使用 {account} 登入並綁定手機 {pre_bound_phone}'):
        login_result = auth_api.login(account, password)
        ws_url = login_result.get('data', {}).get('ws_url')
        if not ws_url:
            raise ValueError(f"為 {account} 登入時，在 Response 中找不到 'ws_url': {login_result}")

        ws_client = AsyncBaseWS(ws_url)
        await ws_client.connect()

        player = PlayerWS(ws_client)
        await player.bind_phone(pre_bound_phone)

    yield pre_bound_phone

    await ws_client.close_connect()


class TestBindPhone:
    @pytest.mark.asyncio
    @pytest.mark.parametrize('case', generate_bind_phone_cases())
    async def test_bind_phone(self, ws_connect: AsyncBaseWS, case: BindPhoneCase):
        player = PlayerWS(ws_connect)
        phone = case.request.telephone
        expected = case.expected
        actual_result = await player.bind_phone(phone)
        verify_case_auto(actual_result, expected)

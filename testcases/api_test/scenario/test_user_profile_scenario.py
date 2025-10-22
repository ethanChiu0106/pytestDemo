"""
執行使用者個人資料完整流程的情境測試。
"""

import logging

import allure
import pytest

from api.auth import AuthAPI
from api.player import PlayerWS
from test_data.api_test_data.scenario.user_profile_scenario import (
    UserProfileScenarioCase,
    generate_user_profile_scenario_cases,
)
from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS
from utils.case_verify_tool import verify_case_auto

logger = logging.getLogger(__name__)


class TestUserProfileScenario:
    @pytest.mark.parametrize('case', generate_user_profile_scenario_cases())
    @pytest.mark.asyncio
    @allure_from_case
    async def test_user_profile_scenario(self, case: UserProfileScenarioCase, auth_api: AuthAPI):
        # 步驟 1: 註冊新帳號
        step_1 = '步驟 1: 註冊新帳號'
        with allure.step(step_1):
            logger.info(step_1)
            register_result = auth_api.register(case.request.account, case.request.initial_password)
            verify_case_auto(register_result, case.expected['register'])

        # 步驟 2: 使用新帳號登入
        step_2 = '步驟 2: 使用新帳號登入'
        with allure.step(step_2):
            logger.info(step_2)
            login_result = auth_api.login(case.request.account, case.request.initial_password)
            verify_case_auto(login_result, case.expected['login'])
            login_data = login_result.get('data')
            token = login_data.get('access_token')
            auth_api.session.headers['Authorization'] = f'Bearer {token}'
            ws_url = login_data.get('ws_url')
            init_name = login_data.get('player_info').get('username')
        # 初始化 WebSocket 連線
        ws = AsyncBaseWS(ws_url)
        await ws.connect()
        player = PlayerWS(ws)
        try:
            # 步驟 3: 驗證初始使用者資料
            step_3 = '步驟 3: 驗證初始使用者資料'
            with allure.step(step_3):
                logger.info(step_3)
                get_info_result = await player.get_player_info()
                verify_case_auto(get_info_result, case.expected['get_initial_info'])
                assert get_info_result['data']['username'] == init_name, '初始使用者名稱有誤'

            # 步驟 4: 變更使用者名稱並驗證
            step_4 = '步驟 4: 變更使用者名稱並驗證'
            with allure.step(step_4):
                logger.info(step_4)
                update_name_result = await player.update_name(case.request.new_name)
                verify_case_auto(update_name_result, case.expected['update_name'])
                assert update_name_result['data']['username'] == case.request.new_name, (
                    f"使用者名稱應為 '{case.request.new_name}'"
                )

        finally:
            await ws.close_connect()

        # 步驟 6: 變更密碼
        step_5 = '步驟 5: 變更密碼'
        with allure.step(step_5):
            logger.info(step_5)
            change_password_result = auth_api.change_password(case.request.initial_password, case.request.new_password)
            verify_case_auto(change_password_result, case.expected['change_password'])

        # 步驟 6: 驗證新密碼有效 (重新登入)
        step_6 = '步驟 6: 驗證新密碼有效'
        with allure.step(step_6):
            logger.info(step_6)
            # 使用新的密碼登入
            verify_login_result = auth_api.login(case.request.account, case.request.new_password)
            verify_case_auto(verify_login_result, case.expected['login'])
            token = verify_login_result.get('data').get('access_token')
            auth_api.session.headers['Authorization'] = f'Bearer {token}'

        # 步驟 7: 還原密碼
        step_7 = '步驟 7: 還原為初始密碼'
        with allure.step(step_7):
            logger.info(step_7)
            revert_password_result = auth_api.change_password(case.request.new_password, case.request.initial_password)
            verify_case_auto(revert_password_result, case.expected['revert_password'])

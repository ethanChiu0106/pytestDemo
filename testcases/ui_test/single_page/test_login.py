import logging

import allure
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from test_data.common.expectations import UI
from test_data.ui_test_data.single.login import UILoginCase, generate_ui_login_cases
from utils.allure_utils import allure_from_case

logger = logging.getLogger(__name__)


class TestLoginPage:
    @pytest.mark.parametrize('case', generate_ui_login_cases())
    @allure_from_case
    def test_login(self, page: Page, case: UILoginCase):
        login_page = LoginPage(page)

        login_page.goto()
        login_page.fill_username(case.request.username)
        login_page.fill_password(case.request.password)
        login_page.click_login_button()

        if case.expected['success']:
            with allure.step('驗證登入成功'):
                login_page.assert_url(UI.INVENTORY_URL_REGEX)
                login_page.assert_element_is_not_visible(login_page.error_msg)
        else:
            with allure.step(f'驗證錯誤訊息: {case.expected["error_message"]}'):
                login_page.assert_element_is_visible(login_page.error_msg)
                login_page.assert_text(login_page.error_msg, case.expected['error_message'])

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.ui_test_data.single.login import UILoginCase, generate_ui_login_cases


class TestLoginPage:
    @pytest.mark.parametrize('case', generate_ui_login_cases())
    def test_login(self, page: Page, case: UILoginCase):
        login_page = LoginPage(page)

        login_page.goto()
        login_page.fill_username(case.request.username)
        login_page.fill_password(case.request.password)
        login_page.click_login_button()

        if case.expected['success']:
            with allure.step('驗證登入成功'):
                InventoryPage(page).expect_loaded()
                expect(login_page.error_msg).to_be_hidden()
        else:
            with allure.step(f'驗證錯誤訊息: {case.expected["error_message"]}'):
                expect(login_page.error_msg).to_have_text(case.expected['error_message'])

import allure

from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = page.get_by_test_id('username')
        self.password_input = page.get_by_test_id('password')
        self.login_button = page.get_by_role('button', name='Login')
        self.error_msg = page.get_by_test_id('error')

    def fill_username(self, username: str):
        with allure.step(f'輸入帳號: {username}'):
            self.username_input.fill(username)

    def fill_password(self, password: str):
        with allure.step('輸入密碼'):
            self.password_input.fill(password)

    def click_login_button(self):
        with allure.step('點擊登入按鈕'):
            self.login_button.click()

    def get_error_message_text(self):
        return self.error_msg.text_content()
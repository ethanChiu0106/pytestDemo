import logging
import re

import allure
from playwright.sync_api import Locator, Page, expect

from utils.config_loader import get_config

logger = logging.getLogger(__name__)


class BasePage:
    """所有頁面物件的基礎類別，封裝了 Playwright 的常用操作。"""

    def __init__(self, page: Page):
        """初始化 BasePage。

        Args:
            page: Playwright 的 Page 物件。
        """
        self.page = page
        self.base_url = get_config().get('urls', {}).get('ui')

    def goto(self, path: str = '', wait_until: str = 'domcontentloaded'):
        """導覽到指定的路徑，如果路徑為空，則前往 base_url。

        Args:
            path: 相對路徑。
            wait_until: 等待的事件，預設為 "domcontentloaded"。
        """
        url = f'{self.base_url}{path}'
        info_text = f'導覽至 URL: {url}'
        logger.info(info_text)
        with allure.step(info_text):
            self.page.goto(url, wait_until=wait_until)

    def assert_text(self, locator: Locator, expected_text: str, message: str = None):
        """驗證指定 Locator 的文字內容是否符合預期。"""
        step_message = message if message else f"驗證: '{locator}' 文字應為 '{expected_text}'"
        with allure.step(step_message):
            expect(locator).to_have_text(expected_text)

    def assert_url(self, url_regex: str, message: str = None):
        """驗證當前 URL 是否符合指定的正規表示式。"""
        step_message = message if message else f"驗證 URL 符合: '{url_regex}'"
        with allure.step(step_message):
            expect(self.page).to_have_url(re.compile(url_regex))

    def assert_element_is_visible(self, locator: Locator, message: str = None):
        """驗證指定的元素是否可見。"""
        step_message = message if message else f"驗證元素 '{locator}' 可見"
        with allure.step(step_message):
            expect(locator).to_be_visible()

    def assert_element_is_not_visible(self, locator: Locator, message: str = None):
        """驗證指定的元素是否不可見。"""
        step_message = message if message else f"驗證元素 '{locator}' 不可見"
        with allure.step(step_message):
            expect(locator).not_to_be_visible()

    def assert_value(self, actual_value, expected_value, message: str):
        """驗證一個實際值是否等於預期值。"""
        with allure.step(message):
            assert actual_value == expected_value, f'{message}: 預期為 {expected_value}, 實際為 {actual_value}'

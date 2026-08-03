import logging
import re

import allure
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


class BasePage:
    """所有頁面物件的基礎類別，封裝了 Playwright 的常用操作。"""

    URL_REGEX: str
    """本頁網址的正規表示式，供 `expect_loaded` 使用；沒有單一網址的頁面不需宣告。"""

    def __init__(self, page: Page):
        """初始化 BasePage。

        Args:
            page: Playwright 的 Page 物件。
        """
        self.page = page

    def goto(self, path: str = '/', wait_until: str = 'domcontentloaded'):
        """導覽到指定的路徑。

        相對路徑會由 Playwright 的 browser context 以 base_url 自動補完，
        base_url 由 `base_url` fixture 提供 (見 testcases/ui_test/conftest.py)。

        Args:
            path: 相對於 base_url 的路徑，預設為網站根目錄。
            wait_until: 等待的事件，預設為 "domcontentloaded"。
        """
        with allure.step(f'導覽至: {path}'):
            self.page.goto(path, wait_until=wait_until)
            logger.info('導覽至 URL: %s', self.page.url)

    def expect_loaded(self):
        """驗證瀏覽器停留在本頁。

        斷的是 `self.URL_REGEX`，所以只能驗證自己那一頁，不會拿 A 頁物件去斷 B 頁網址。
        """
        with allure.step(f'驗證停留在 {type(self).__name__}'):
            expect(self.page).to_have_url(re.compile(self.URL_REGEX))

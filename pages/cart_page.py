import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CartPage(BasePage):
    """購物車頁面的 Page Object。"""

    URL_REGEX = '.*cart.html'

    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_item = self.page.get_by_test_id('inventory-item')
        self.checkout_button = self.page.get_by_test_id('checkout')

    @allure.step('點擊「Checkout」按鈕')
    def click_checkout(self):
        """點擊結帳按鈕。"""
        self.checkout_button.click()

    def expect_has_item(self, product_name: str):
        """驗證指定商品在購物車中。

        Args:
            product_name: 商品名稱。
        """
        with allure.step(f"驗證購物車包含商品 '{product_name}'"):
            expect(self.cart_item.filter(has_text=product_name)).to_be_visible()

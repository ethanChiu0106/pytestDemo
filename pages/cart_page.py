import allure
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """購物車頁面的 Page Object。"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_item = self.page.get_by_test_id('inventory-item')
        self.checkout_button = self.page.get_by_test_id('checkout')

    def get_item_by_name(self, product_name: str) -> Locator:
        """根據商品名稱，獲取購物車中對應的項目定位器。"""
        allure.step("從購物車中尋找商品 '{product_name}'")
        return self.cart_item.filter(has_text=product_name)

    @allure.step('點擊「Checkout」按鈕')
    def click_checkout(self):
        """點擊結帳按鈕。"""
        self.checkout_button.click()

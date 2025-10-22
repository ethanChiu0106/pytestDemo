import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """商品列表頁面的 Page Object。"""

    def __init__(self, page: Page):
        super().__init__(page)
        self._item_container = self.page.get_by_test_id('inventory-item')
        self.shopping_cart_badge = self.page.get_by_test_id('shopping-cart-badge')
        self.shopping_cart_link = self.page.get_by_test_id('shopping-cart-link')

    def add_product_to_cart(self, product_name: str):
        """點擊指定商品的「Add to cart」按鈕。"""
        with allure.step(f"將商品 '{product_name}' 加入購物車"):
            product_container = self._item_container.filter(has_text=product_name)
            add_button = product_container.locator('[data-test^="add-to-cart-"]')
            add_button.click()

    def get_cart_badge_count(self) -> str:
        """獲取購物車圖示上的數量。如果圖示不可見，則回傳 '0'。"""
        with allure.step('獲取購物車中的商品數量'):
            if not self.shopping_cart_badge.is_visible():
                return '0'
            return self.shopping_cart_badge.text_content()

    def goto_shopping_cart_page(self):
        self.shopping_cart_link.click()

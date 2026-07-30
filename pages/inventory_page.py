import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """商品列表頁面的 Page Object。"""

    URL_REGEX = '.*inventory.html'

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

    def goto_shopping_cart_page(self):
        self.shopping_cart_link.click()

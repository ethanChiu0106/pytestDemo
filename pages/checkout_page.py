import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """結帳流程相關頁面的 Page Object。"""

    def __init__(self, page: Page):
        super().__init__(page)
        # --- Step One: Your Information ---
        self.first_name_input = self.page.get_by_test_id('firstName')
        self.last_name_input = self.page.get_by_test_id('lastName')
        self.postal_code_input = self.page.get_by_test_id('postalCode')
        self.continue_button = self.page.get_by_test_id('continue')

        # --- Step Two: Overview ---
        self._product_quantity = self.page.get_by_test_id('item-quantity')
        self._product_name = self.page.get_by_test_id('inventory-item-name')
        self._payment_info_value = self.page.get_by_test_id('payment-info-value')
        self._shipping_info_value = self.page.get_by_test_id('shipping-info-value')
        self._item_total_value = self.page.get_by_test_id('subtotal-label')
        self._tax_value = self.page.get_by_test_id('tax-label')
        self._final_total_value = self.page.get_by_test_id('total-label')
        self.finish_button = self.page.get_by_test_id('finish')

        # --- Complete ---
        self.complete_header = self.page.get_by_test_id('complete-header')
        self.complete_text = self.page.get_by_test_id('complete-text')
        self.back_home_button = self.page.get_by_test_id('back-to-products')

    @allure.step('填寫結帳資訊')
    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str):
        """在結帳第一步填寫使用者資訊。"""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    @allure.step('點擊「Continue」按鈕')
    def click_continue(self):
        """點擊繼續按鈕，前往結帳第二步。"""
        self.continue_button.click()

    @allure.step('點擊「Finish」按鈕完成結帳')
    def click_finish(self):
        """點擊完成按鈕。"""
        self.finish_button.click()

    @allure.step('點擊「Back Home」按鈕')
    def click_back_home(self):
        """點擊返回首頁按鈕。"""
        self.back_home_button.click()

    def get_payment_info(self) -> str:
        """獲取付款資訊"""
        return self._payment_info_value.text_content()

    def get_shipping_info(self) -> str:
        """獲取運送資訊"""
        return self._shipping_info_value.text_content()

    def get_item_total(self) -> str:
        """獲取商品總額 (Item total)，並移除標籤和貨幣符號"""
        full_text = self._item_total_value.text_content()
        return full_text.replace('Item total: $', '').strip()

    def get_tax(self) -> str:
        """獲取稅金 (Tax)，並移除標籤和貨幣符號"""
        full_text = self._tax_value.text_content()
        return full_text.replace('Tax: $', '').strip()

    def get_final_total(self) -> str:
        """獲取最終總計 (Total)，並移除標籤和貨幣符號"""
        full_text = self._final_total_value.text_content()
        return full_text.replace('Total: $', '').strip()

import math
import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """結帳流程相關頁面的 Page Object。"""

    STEP_ONE_URL_REGEX = '.*checkout-step-one.html'
    STEP_TWO_URL_REGEX = '.*checkout-step-two.html'
    COMPLETE_URL_REGEX = '.*checkout-complete.html'

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
        self._complete_header = self.page.get_by_test_id('complete-header')
        self._complete_text = self.page.get_by_test_id('complete-text')
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

    def get_item_total(self) -> str:
        """獲取商品總額 (Item total)，並移除標籤和貨幣符號"""
        return self._item_total_value.inner_text().replace('Item total: $', '').strip()

    def get_tax(self) -> str:
        """獲取稅金 (Tax)，並移除標籤和貨幣符號"""
        return self._tax_value.inner_text().replace('Tax: $', '').strip()

    def get_final_total(self) -> str:
        """獲取最終總計 (Total)，並移除標籤和貨幣符號"""
        return self._final_total_value.inner_text().replace('Total: $', '').strip()

    def expect_info_step(self):
        """驗證停留在結帳資訊頁 (step one)。"""
        with allure.step('驗證進入結帳資訊頁面'):
            expect(self.page).to_have_url(re.compile(self.STEP_ONE_URL_REGEX))

    def expect_summary(self, details: dict):
        """驗證結帳總覽頁的商品、金流與金額資訊。

        Args:
            details: 預期值，需含 quantity / product_name / payment_info /
                shipping_info / item_total / tax / final_total。
        """
        with allure.step('驗證結帳總覽頁面的所有資訊'):
            expect(self.page).to_have_url(re.compile(self.STEP_TWO_URL_REGEX))
            expect(self._product_quantity).to_have_text(details['quantity'])
            expect(self._product_name).to_have_text(details['product_name'])
            expect(self._payment_info_value).to_have_text(details['payment_info'])
            expect(self._shipping_info_value).to_have_text(details['shipping_info'])

            item_total, tax, final_total = self.get_item_total(), self.get_tax(), self.get_final_total()
            assert item_total == details['item_total'], f'商品總額: 預期 {details["item_total"]}, 實際 {item_total}'
            assert tax == details['tax'], f'稅金: 預期 {details["tax"]}, 實際 {tax}'
            assert final_total == details['final_total'], f'最終總計: 預期 {details["final_total"]}, 實際 {final_total}'
            assert math.isclose(float(item_total) + float(tax), float(final_total), abs_tol=0.01), (
                f'{item_total} + {tax} 應等於 {final_total}'
            )

    def expect_complete(self, details: dict):
        """驗證訂單完成頁的標題與訊息。

        Args:
            details: 預期值，需含 complete_header / complete_text。
        """
        with allure.step('驗證訂單完成訊息'):
            expect(self.page).to_have_url(re.compile(self.COMPLETE_URL_REGEX))
            expect(self._complete_header).to_have_text(details['complete_header'])
            expect(self._complete_text).to_have_text(details['complete_text'])

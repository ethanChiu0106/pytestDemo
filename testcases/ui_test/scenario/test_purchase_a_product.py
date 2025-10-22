import logging

import allure
import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.common.expectations import UI
from test_data.ui_test_data.scenario.purchase import UIPurchaseCase, generate_ui_purchase_cases
from utils.allure_utils import allure_from_case

logger = logging.getLogger(__name__)


class TestProductPurchase:
    @pytest.mark.parametrize('case', generate_ui_purchase_cases())
    @allure_from_case
    def test_purchase_a_product_successfully(self, page: Page, case: UIPurchaseCase):
        """測試一個完整的商品購買流程。"""
        login_page = LoginPage(page)
        inventory_page = InventoryPage(page)
        cart_page = CartPage(page)
        checkout_page = CheckoutPage(page)
        details_expected = case.expected['details']

        # 步驟 1: 前往登入頁面
        login_page.goto()

        # 步驟 2: 登入
        with allure.step('使用 standard_user 登入'):
            login_page.fill_username(case.request.username)
            login_page.fill_password(case.request.password)
            login_page.click_login_button()

        # 步驟 3: 瀏覽商品 (斷言)
        inventory_page.assert_url(UI.INVENTORY_URL_REGEX, '驗證是否成功登入並跳轉到商品頁')

        # 步驟 4: 加入購物車
        item_to_purchase = case.request.product_name
        inventory_page.add_product_to_cart(item_to_purchase)
        inventory_page.assert_text(
            inventory_page.shopping_cart_badge,
            UI.Purchase.PURCHASE_QUANTITY,
            f'驗證購物車圖示數量為 {UI.Purchase.PURCHASE_QUANTITY}',
        )

        # 步驟 5: 驗證購物車
        inventory_page.goto_shopping_cart_page()
        cart_page.assert_url(UI.Purchase.CART_URL_REGEX, '驗證是否進入購物車頁面')
        cart_page.assert_element_is_visible(
            cart_page.get_item_by_name(item_to_purchase), f"驗證商品 '{item_to_purchase}' 是否在購物車中"
        )

        # 步驟 6: 結帳與填寫資訊
        cart_page.click_checkout()
        checkout_page.assert_url(UI.Purchase.CHECKOUT_STEP_ONE_URL_REGEX, '驗證是否進入結帳資訊頁面')
        checkout_page.fill_checkout_info(
            first_name=case.request.first_name,
            last_name=case.request.last_name,
            postal_code=case.request.postal_code,
        )
        checkout_page.click_continue()

        # 步驟 7: 確認結帳資訊
        checkout_page.assert_url(UI.Purchase.CHECKOUT_STEP_TWO_URL_REGEX, '驗證是否進入結帳總覽頁面')
        with allure.step('驗證結帳總覽頁面的所有資訊'):
            checkout_page.assert_text(checkout_page._product_quantity, UI.Purchase.PURCHASE_QUANTITY)
            checkout_page.assert_text(checkout_page._product_name, details_expected['product_name'])
            checkout_page.assert_text(checkout_page._payment_info_value, details_expected['payment_info'])
            checkout_page.assert_text(checkout_page._shipping_info_value, details_expected['shipping_info'])

            item_total = checkout_page.get_item_total()
            checkout_page.assert_value(
                item_total, details_expected['item_total'], f'商品總額應為 {details_expected["item_total"]}'
            )

            tax = checkout_page.get_tax()
            checkout_page.assert_value(tax, details_expected['tax'], f'稅金應為 {details_expected["tax"]}')

            final_total = checkout_page.get_final_total()
            checkout_page.assert_value(
                final_total, details_expected['final_total'], f'最終總計應為 {details_expected["final_total"]}'
            )

            with allure.step('驗證商品總額 + 稅金 = 最終總計'):
                assert float(item_total) + float(tax) == pytest.approx(float(final_total))

        # 步驟 8: 完成結帳
        checkout_page.click_finish()
        checkout_page.assert_url(UI.Purchase.CHECKOUT_COMPLETE_URL_REGEX, '驗證是否進入結帳完成頁面')
        with allure.step('驗證訂單完成訊息'):
            checkout_page.assert_text(checkout_page.complete_header, details_expected['complete_header'])
            checkout_page.assert_text(checkout_page.complete_text, details_expected['complete_text'])

        # 步驟 9: 回到商品頁面，購物車應被清空
        checkout_page.click_back_home()
        inventory_page.assert_url(UI.INVENTORY_URL_REGEX, '驗證回到商品頁面')
        inventory_page.assert_element_is_not_visible(inventory_page.shopping_cart_badge, '驗證購物車為空')

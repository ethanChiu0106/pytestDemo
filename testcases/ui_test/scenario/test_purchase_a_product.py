import allure
import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.ui_test_data.scenario.purchase import UIPurchaseCase, generate_ui_purchase_cases


class TestProductPurchase:
    @pytest.mark.parametrize('case', generate_ui_purchase_cases())
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
        inventory_page.expect_loaded()

        # 步驟 4: 加入購物車
        item_to_purchase = case.request.product_name
        inventory_page.add_product_to_cart(item_to_purchase)
        expect(inventory_page.shopping_cart_badge).to_have_text(details_expected['quantity'])

        # 步驟 5: 驗證購物車
        inventory_page.goto_shopping_cart_page()
        cart_page.expect_loaded()
        cart_page.expect_has_item(item_to_purchase)

        # 步驟 6: 結帳與填寫資訊
        cart_page.click_checkout()
        checkout_page.expect_info_step()
        checkout_page.fill_checkout_info(
            first_name=case.request.first_name,
            last_name=case.request.last_name,
            postal_code=case.request.postal_code,
        )
        checkout_page.click_continue()

        # 步驟 7: 確認結帳資訊
        checkout_page.expect_summary(details_expected)

        # 步驟 8: 完成結帳
        checkout_page.click_finish()
        checkout_page.expect_complete(details_expected)

        # 步驟 9: 回到商品頁面，購物車應被清空
        checkout_page.click_back_home()
        inventory_page.expect_loaded()
        expect(inventory_page.shopping_cart_badge).to_be_hidden()

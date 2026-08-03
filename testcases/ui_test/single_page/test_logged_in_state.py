import logging

import pytest
from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage

logger = logging.getLogger(__name__)


class TestLoggedInState:
    @pytest.mark.single
    def test_directly_on_inventory_without_login(self, logged_in_page: Page):
        """驗證載入 storage_state 後可直接進入商品頁，不需重新登入"""
        inventory = InventoryPage(logged_in_page)
        inventory.goto('/inventory.html')

        inventory.expect_loaded()
        inventory.add_product_to_cart('Sauce Labs Fleece Jacket')
        expect(inventory.shopping_cart_badge).to_have_text('1')

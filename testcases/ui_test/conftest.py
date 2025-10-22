import logging

import allure
import pytest
from playwright.sync_api import Playwright

# 獲取 logger 實例
logger = logging.getLogger(__name__)


@pytest.fixture(scope='package', autouse=True)
def add_ui_url_to_allure_report(test_config: dict, shared_used_urls: set):
    """自動將 UI base URL 添加到共用 URL 集合中，以便寫入 Allure 報告。"""
    ui_url = test_config.get('urls', {}).get('ui')
    if ui_url:
        shared_used_urls.add(ui_url)


@pytest.fixture(scope='session', autouse=True)
def setup_ui_test_id(playwright: Playwright):
    """
    為 Playwright 設定自訂的 `test-id` 屬性 (`data-test`)
    """
    test_id = 'data-test'
    with allure.step(f'設定 test-id 屬性為 {test_id}'):
        playwright.selectors.set_test_id_attribute(test_id)

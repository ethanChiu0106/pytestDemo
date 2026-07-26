import logging

import allure
import pytest
from playwright.sync_api import Playwright

# 獲取 logger 實例
logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def base_url(request: pytest.FixtureRequest, test_config: dict) -> str:
    """提供 UI 測試的 base URL。

    此 fixture 覆寫 pytest-base-url 的同名 fixture，pytest-playwright 會將它
    寫入 browser context 的 `base_url`，因此 Page Object 中只需使用相對路徑。

    優先序: `--base-url` 命令列參數 > 設定檔的 `urls.ui`。

    Args:
        request: pytest 的 request 物件，用於讀取命令列參數。
        test_config: 當前環境的測試設定。

    Returns:
        UI 測試的 base URL。
    """
    cli_base_url = request.config.getoption('base_url')
    if cli_base_url:
        logger.info('使用命令列指定的 base URL: %s', cli_base_url)
        return cli_base_url

    ui_url = test_config.get('urls', {}).get('ui')
    if not ui_url:
        env = request.config.getoption('--env')
        pytest.fail(f"環境 '{env}' 的設定檔中缺少 'urls.ui'，UI 測試無法取得 base URL。")
    return ui_url


@pytest.fixture(scope='package', autouse=True)
def add_ui_url_to_allure_report(base_url: str, shared_used_urls: set):
    """自動將 UI base URL 添加到共用 URL 集合中，以便寫入 Allure 報告。"""
    shared_used_urls.add(base_url)


@pytest.fixture(scope='session', autouse=True)
def setup_ui_test_id(playwright: Playwright):
    """
    為 Playwright 設定自訂的 `test-id` 屬性 (`data-test`)
    """
    test_id = 'data-test'
    with allure.step(f'設定 test-id 屬性為 {test_id}'):
        playwright.selectors.set_test_id_attribute(test_id)

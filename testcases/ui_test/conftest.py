import logging

import allure
import pytest
from playwright.sync_api import Playwright

from utils.config_loader import get_config

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def base_url(request: pytest.FixtureRequest) -> str:
    """提供 UI 測試的 base URL。

    此 fixture 覆寫 pytest-base-url 的同名 fixture，pytest-playwright 會將它
    寫入 browser context 的 `base_url`，因此 Page Object 中只需使用相對路徑。

    優先序: `--base-url` 命令列參數 > 設定檔的 `urls.ui`。

    Args:
        request: pytest 的 request 物件，用於讀取命令列參數。

    Returns:
        UI 測試的 base URL。

    Raises:
        ConfigError: 如果未指定 `--base-url`，且當前環境的設定中沒有 `urls.ui`。
    """
    cli_base_url = request.config.getoption('base_url')
    if cli_base_url:
        logger.info('使用命令列指定的 base URL: %s', cli_base_url)
        return cli_base_url

    return get_config().url('ui')


@pytest.fixture(scope='session', autouse=True)
def setup_ui_test_id(playwright: Playwright):
    """
    為 Playwright 設定自訂的 `test-id` 屬性 (`data-test`)
    """
    test_id = 'data-test'
    with allure.step(f'設定 test-id 屬性為 {test_id}'):
        playwright.selectors.set_test_id_attribute(test_id)

import logging
from pathlib import Path

import allure
import pytest

from test_data.common.base import TestCaseData
from utils.allure_reporting import write_allure_metadata
from utils.config_loader import get_config, set_current_env

# pytest 只改寫測試檔與 conftest 內的斷言。不註冊的話，`case_verify_tool` 裡的
# 比對失敗只會拋出光禿禿的 `AssertionError`，看不到實際值與預期值的差異。
# 必須在該模組被 import 前呼叫，因此放在 conftest 的最上層。
pytest.register_assert_rewrite('utils.case_verify_tool')

logger = logging.getLogger(__name__)


# --- Pytest Hooks ---


def pytest_addoption(parser):
    """為 pytest 新增 `--env` 命令列參數。

    Args:
        parser: pytest 的命令列參數解析器。
    """
    parser.addoption('--env', default='qa', choices=['dev', 'qa'], help='environment parameter')


def pytest_configure(config):
    """在測試開始時，設定要使用的環境名稱

    Args:
        config: pytest 的設定物件。
    """
    env = config.getoption('--env')
    set_current_env(env)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """套用 case 的 Allure 標題與描述，並記錄測項的開始與結束。

    Allure 標籤是**被迫**放在 call 階段：`allure.title` 不是 MarkDecorator，不能像
    其他標籤那樣透過 `create_param_from_case` 掛成 pytest.param 的 mark；而
    `allure.dynamic` 寫在 fixture (setup 階段) 不會有作用，只能用 hookwrapper。
    此寫法對 sync 與 async 測試皆適用。

    日誌是**刻意**放在 call 階段：「開始/結束執行測項」要框住的是測項本身，登入等
    前置條件 (setup 階段) 與密碼還原等清理 (teardown 階段) 都排除在外。改成 autouse
    fixture 會讓它排到最前面，導致前置條件被框進來。

    Args:
        item: 當前執行的測試項目。僅處理參數名為 `case`、型別為 `TestCaseData` 的 parametrize。
    """
    callspec = getattr(item, 'callspec', None)
    case = callspec.params.get('case') if callspec else None
    if isinstance(case, TestCaseData):
        if case.title:
            allure.dynamic.title(case.title)
        if case.description:
            allure.dynamic.description(case.description)

    logger.info('*************** 開始執行測項 ***************')
    yield
    logger.info('*************** 結束執行測項 ***************')


@pytest.fixture(scope='session', autouse=True)
def allure_environment_setup(request: pytest.FixtureRequest):
    """在測試 session 結束後，收集報告所需的中繼資料並寫入 Allure 結果目錄。

    位址取自當前環境的設定，而非執行期收集——Allure 的環境區塊描述的是
    「這份報告打的是哪個環境」，屬於整個 launch 不變的資訊。逐次請求打了什麼
    已記錄在各測項的 step 與 log 中。
    """
    yield
    config = get_config()
    urls = dict(config.urls)
    cli_base_url = request.config.getoption('base_url', None)
    if cli_base_url:
        urls['ui'] = cli_base_url
    urls_str = ', '.join(f'{name}={url}' for name, url in sorted(urls.items()))
    base_path = Path(__file__).resolve().parent
    write_allure_metadata(config.env, urls_str, base_path)

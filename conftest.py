import logging
import platform
import shutil
from pathlib import Path

import pytest

from utils.config_loader import get_config, set_current_env

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


# --- 核心 Fixtures ---


@pytest.fixture(scope='session')
def test_config() -> dict:
    """提供 session 範圍的測試設定檔內容。

    Returns:
        一個包含所有測試設定的字典。
    """
    return get_config()


@pytest.fixture(scope='session')
def shared_used_urls() -> set:
    """提供一個共用集合，用於記錄所有在測試中使用過的 URL。

    Returns:
        一個 session 範圍的空集合。
    """
    return set()


# --- 其他 Hooks ---


def write_allure_environment(environment_name: str, url: str, base_path: Path):
    """將環境資訊寫入 Allure 報告用的 `environment.properties` 檔案。

    Args:
        environment_name: 當前測試環境的名稱 (例如 'qa', 'dev')。
        url: 測試過程中使用的主要服務 URL。
        base_path: 專案的根目錄路徑。
    """
    allure_result_path = base_path / 'allure-results'
    source_executor_path = base_path / 'executor.json'
    allure_result_path.mkdir(parents=True, exist_ok=True)
    environment_path = allure_result_path / 'environment.properties'
    with open(environment_path, 'w') as f:
        f.write(f'os={platform.system()}\n')
        f.write(f'python_version={platform.python_version()}\n')
        f.write(f'environment={environment_name}, {url}\n')
    if source_executor_path.exists():
        shutil.copy(source_executor_path, allure_result_path)


@pytest.fixture(scope='session', autouse=True)
def allure_environment_setup(request: pytest.FixtureRequest, shared_used_urls: set):
    """在測試 session 結束後，收集環境資訊並寫入 Allure 報告。"""
    yield
    env = request.config.getoption('--env')
    used_urls_str = ', '.join(sorted(list(shared_used_urls)))
    if not used_urls_str:
        used_urls_str = 'No clients were used in this test run.'
    base_path = Path(__file__).resolve().parent
    write_allure_environment(env, used_urls_str, base_path)


@pytest.fixture
def test_case_setup_and_teardown():
    """在每個測試案例執行前後，印出開始與結束的日誌。"""
    logger.info('*************** 開始執行測項 ***************')
    yield
    logger.info('*************** 結束執行測項 ***************')


def pytest_collection_modifyitems(items):
    """修改 pytest 收集到的所有測試案例。

    主要用於自動為所有測試案例加上 `test_case_setup_and_teardown` fixture。

    Args:
        items: pytest 收集到的所有測試案例物件列表。
    """
    for item in items:
        if 'test_case_setup_and_teardown' not in item.fixturenames:
            item.fixturenames.append('test_case_setup_and_teardown')

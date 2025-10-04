import logging
import platform
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Type, TypedDict, TypeVar

import allure
import pytest
import pytest_asyncio
import requests

from api.auth import AuthAPI
from test_data.common.expectations import HTTP
from utils.api_provider import ApiClientProvider
from utils.async_base_ws import AsyncBaseWS
from utils.config_loader import get_config, set_current_env

logger = logging.getLogger(__name__)
T = TypeVar('T')


class UserDict(TypedDict):
    account: str
    password: str


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
def user_creator(auth_api: AuthAPI, test_config: dict) -> Callable[[str], None]:
    """提供一個用於建立測試使用者的工廠函式。

    將建立使用者所需的 `auth_api` 和 `test_config` 依賴包裝起來，
    回傳一個更簡單的函式，方便在各個 setup fixture 中重複使用。

    Args:
        auth_api: 用於呼叫註冊 API 的 `AuthAPI` 物件。
        test_config: 包含使用者設定的字典。

    Returns:
        一個工廠函式，接收 `user_key` 字串，用於建立指定的使用者。
    """

    def _creator(user_key: str):
        user_config = test_config.get('users', {}).get(user_key)
        if not user_config:
            logger.warning(f"\nWarning: 在 secrets.yml 中找不到 user key '{user_key}'，跳過建立。")
            return

        account = user_config['account']
        password = user_config['password']
        logger.info(f"\n建立帳號 '{account}' (來自: {user_key})...")

        result = auth_api.register(account, password)

        if result.get('code') == HTTP.Auth.Register.SUCCESS['code']:
            logger.info(f"帳號 '{account}' 創建成功")
        elif result.get('code') == HTTP.Auth.Register.REPEATED_ACCOUNT['code']:
            logger.info(f"帳號 '{account}' 已存在")
        else:
            logger.warning(f"建置帳號 '{account}' 時發生錯誤: {result}")

    return _creator


@pytest.fixture(scope='session', autouse=True)
def setup_default_user(user_creator: Callable[[str], None]):
    """在測試開始前，自動建立預設的測試帳號。"""
    logger.info('開始建立預設帳號...')
    user_creator('default_user')


@pytest.fixture(scope='session')
def setup_change_password_user(user_creator: Callable[[str], None]):
    """為密碼變更測試，建立專用的測試帳號。"""
    user_creator('change_password_user')


@pytest.fixture(scope='session')
def setup_duplicate_phone_user(user_creator: Callable[[str], None]):
    """為手機綁定測試，建立專用的測試帳號。"""
    user_creator('duplicate_phone_user')


@pytest.fixture(scope='session')
def shared_session() -> Generator[requests.Session, Any, None]:
    """提供一個在整個測試 session 中共用的 `requests.Session` 物件。

    Yields:
        一個 `requests.Session` 物件，用於共用連線。
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope='session')
def api_factory(shared_session: requests.Session) -> Callable:
    """提供一個建立 API Client 的工廠函式。

    Args:
        shared_session: 共用的 `requests.Session` 物件。

    Returns:
        一個工廠函式，接收 `api_class` 與 `base_url`，用於建立 Client 物件。
    """

    def _factory(api_class: Type[T], base_url: str) -> T:
        return api_class(base_url=base_url, session=shared_session)

    return _factory


@pytest.fixture(scope='session')
def shared_used_urls() -> set:
    """提供一個共用集合，用於記錄所有在測試中使用過的 URL。

    Returns:
        一個 session 範圍的空集合。
    """
    return set()


@pytest.fixture(scope='session')
def api_provider(api_factory: Callable, shared_used_urls: set, test_config: dict) -> ApiClientProvider:
    """提供 API Client 的中心服務提供者。

    組合 `test_config` 的網址和 `api_factory` 的建立邏輯，
    為測試提供獲取 API Client 的統一入口。

    Args:
        api_factory: 用於建立 API Client 物件的函式。
        shared_used_urls: 用於記錄已使用 URL 的共用集合。
        test_config: 包含所有測試設定的字典。

    Returns:
        一個已設定好的 `ApiClientProvider` 物件。
    """
    env_urls = test_config.get('urls', {})
    return ApiClientProvider(api_factory, env_urls, shared_used_urls)


# --- 便利 API Fixtures ---


@pytest.fixture(scope='session')
def auth_api(api_provider: ApiClientProvider) -> AuthAPI:
    """提供一個 session 範圍的 `AuthAPI` 物件。

    Args:
        api_provider: API Client 的中心服務提供者。

    Returns:
        一個 `AuthAPI` 物件。
    """
    return api_provider.get(AuthAPI)


@pytest.fixture
def user_data(request: pytest.FixtureRequest, test_config: dict) -> UserDict:
    """根據測試參數或預設值，提供使用者資料。

    此 fixture 支援透過 `@pytest.mark.parametrize` 間接傳入參數，並有以下處理邏輯：
    - **當參數是字典 (dict):** 直接回傳該字典作為使用者資料，並驗證其格式。
    - **當參數是字串 (str):** 將該字串視為 `user_key`，並從設定檔中查找對應的使用者資料。
    - **當沒有參數時:** 回傳預設的 `default_user` 資料。

    Args:
        request: pytest 的 request 物件，用於獲取 `parametrize` 傳入的參數。
        test_config: 包含所有使用者設定的字典。

    Returns:
        一個包含使用者帳號密碼的字典。

    Raises:
        pytest.fail: 如果傳入的 dict 格式錯誤，或找不到指定的使用者 key。
    """
    if hasattr(request, 'param'):
        param = request.param
        users = test_config['users']

        if isinstance(param, dict):
            if 'account' not in param or 'password' not in param:
                pytest.fail("parametrize dict key必須包含 'account' 和 'password'")
            return param
        elif isinstance(param, str):
            user_key = param
            user = users.get(user_key)
            if not user:
                pytest.fail(f"在 secrets.yml 中找不到透過參數傳入的 user key: '{user_key}'")
            return user

    default_user = test_config.get('users', {}).get('default_user')
    if not default_user:
        pytest.fail("在 secrets.yml 的 'users' 中找不到預設的 'default_user'")

    return default_user


# --- 預登入 Fixtures ---
@pytest.fixture
def pre_login(user_data: UserDict, auth_api: AuthAPI) -> Generator[AuthAPI, None, None]:
    """為測試案例預先登入，並在 `AuthAPI` 物件中設定 token。

    Args:
        user_data: 使用者的帳號密碼資料。
        auth_api: 用於執行登入的 `AuthAPI` 物件。

    Yields:
        一個已登入並包含 `Authorization` header 的 `AuthAPI` 物件。

    Raises:
        ValueError: 如果登入失敗或回傳結果中沒有 token。
    """
    account, password = user_data['account'], user_data['password']
    with allure.step(f'前置步驟 => {account} 登入'):
        result = auth_api.login(account, password)
        if result.get('status_code') != 200:
            raise ValueError(f'pre_login 失敗 Account:{account} \n{result}')
        token = result.get('data', {}).get('access_token')
        if not token:
            raise ValueError(f'登入 response 不含 token: {result}')
        auth_api.session.headers['Authorization'] = f'Bearer {token}'
        auth_api.login_result = result
    yield auth_api


@pytest_asyncio.fixture
async def ws_connect(auth_api: AuthAPI, user_data: UserDict) -> AsyncIterator[AsyncBaseWS]:
    """提供一個已連線的 WebSocket 物件。

    Args:
        auth_api: 用於登入以獲取 WebSocket URL 的 `AuthAPI` 物件。
        user_data: 登入所需的使用者資料。

    Yields:
        一個已連線的 `AsyncBaseWS` 物件。

    Raises:
        ValueError: 如果登入後找不到 WebSocket URL。
    """
    result = auth_api.login(user_data['account'], user_data['password'])
    ws_url = result.get('data', {}).get('ws_url')
    if not ws_url:
        raise ValueError(f"登入成功，但在Response中找不到 'ws_url': {result}")

    with allure.step('WS connect'):
        ws_client = AsyncBaseWS(ws_url)
        await ws_client.connect()
    yield ws_client
    await ws_client.close_connect()


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

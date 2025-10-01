import logging
import platform
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Type, TypeVar

import allure
import pytest
import pytest_asyncio
import requests

from api.auth import AuthAPI
from api.item import Item
from test_data.common.expectations import Auth
from utils.api_provider import ApiClientProvider
from utils.async_base_ws import AsyncBaseWS
from utils.config_loader import get_config, load_test_config

logger = logging.getLogger(__name__)
T = TypeVar('T')


# --- Pytest Hooks ---


def pytest_addoption(parser):
    """定義 --env 命令列參數。"""
    parser.addoption('--env', default='qa', choices=['dev', 'qa'], help='environment parameter')


def pytest_configure(config):
    """在測試啟動時執行一次，讀取 --env 並將設定載入到全域變數中。"""
    env = config.getoption('--env')
    load_test_config(env)


# --- 核心 Fixtures ---


@pytest.fixture(scope='session')
def test_config() -> dict:
    """提供一個 session 範圍的設定資料。"""
    return get_config()


@pytest.fixture(scope='session')
def user_creator(auth_api: AuthAPI, test_config: dict) -> Callable[[str], None]:
    """
    提供一個「使用者建立工廠」函式 (Fixture Factory Pattern)。

    這個 fixture 將建立使用者所需的所有依賴 (auth_api, test_config) 包裝起來，
    並回傳一個只需要傳入 `user_key` 的簡單函式。
    這麼做是為了讓其他的 setup fixtures (如 setup_default_user) 變得更簡潔，
    並將建立使用者的核心邏輯集中管理。

    :return: 一個可呼叫的工廠函式，簽名為 `(user_key: str) -> None`。
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

        if result.get('code') == Auth.Register.SUCCESS['code']:
            logger.info(f"帳號 '{account}' 創建成功")
        elif result.get('code') == Auth.Register.REPEATED_ACCOUNT['code']:
            logger.info(f"帳號 '{account}' 已存在")
        else:
            logger.warning(f"建置帳號 '{account}' 時發生錯誤: {result}")

    return _creator


@pytest.fixture(scope='session', autouse=True)
def setup_default_user(user_creator: Callable[[str], None]):
    """
    一個 session 範圍且自動執行的 fixture。

    它的作用是在所有測試開始前，確保設定檔中定義的 'default_user'
    已經被註冊，為大多數測試提供一個可用的預設帳號。
    """
    logger.info('開始建立預設帳號...')
    user_creator('default_user')


@pytest.fixture(scope='session')
def setup_change_password_user(user_creator: Callable[[str], None]):
    """
    一個 session 範圍的 fixture，用於建立密碼變更測試所需的專用帳號。

    注意：此 fixture **不會**自動執行。
    只有當測試案例明確地將 `setup_change_password_user` 作為參數時，
    它才會被觸發以建立指定的使用者。
    """
    user_creator('change_password_user')


@pytest.fixture(scope='session')
def setup_duplicate_phone_user(user_creator: Callable[[str], None]):
    """
    一個 session 範圍的 fixture，用於建立手機綁定測試所需的專用帳號。
    """
    user_creator('duplicate_phone_user')


@pytest.fixture(scope='session')
def shared_session() -> Generator[requests.Session, Any, None]:
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope='session')
def api_factory(shared_session: requests.Session):
    def _factory(api_class: Type[T], base_url: str) -> T:
        return api_class(base_url=base_url, session=shared_session)

    return _factory


@pytest.fixture(scope='session')
def shared_used_urls() -> set:
    return set()


@pytest.fixture(scope='session')
def api_provider(api_factory, shared_used_urls, test_config: dict) -> ApiClientProvider:
    """提供 ApiClientProvider 實例，直接從全域設定獲取 URLs。"""
    env_urls = test_config.get('urls', {})
    return ApiClientProvider(api_factory, env_urls, shared_used_urls)


# --- 便利 API Fixtures ---


@pytest.fixture(scope='session')
def auth_api(api_provider: ApiClientProvider) -> AuthAPI:
    """
    提供一個 session 生命週期的 AuthAPI 客戶端實例。
    """
    return api_provider.get(AuthAPI)


@pytest.fixture
def user_data(request: pytest.FixtureRequest, test_config: dict) -> dict:
    """
    根據 parametrize 或預設值提供使用者資料。
    - 如果案例使用 parametrize (indirect=True)，則使用傳入的參數。
    - 參數可以是 string (在 secrets.yml 中的 user key)。
    - 參數可以是 dict (直接使用該使用者資料)。
    - 否則，回傳 'default_user' 的資料。
    """
    if hasattr(request, 'param'):
        param = request.param
        users = test_config['users']

        if isinstance(param, dict):
            # 直接使用傳入的 dict
            return param
        elif isinstance(param, str):
            # 使用傳入的 string 作為 key 查詢使用者
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
def pre_login(user_data: dict, auth_api: AuthAPI) -> Generator[AuthAPI, None, None]:
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
async def ws_connect(auth_api: AuthAPI, user_data: dict) -> AsyncIterator[AsyncBaseWS]:
    """提供一個已連線的 ws 物件，並在測試後自動關閉。"""
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
    yield
    env = request.config.getoption('--env')
    used_urls_str = ', '.join(sorted(list(shared_used_urls)))
    if not used_urls_str:
        used_urls_str = 'No clients were used in this test run.'
    base_path = Path(__file__).resolve().parent
    write_allure_environment(env, used_urls_str, base_path)


@pytest.fixture
def test_case_setup_and_teardown():
    logger.info('*************** 開始執行測項 ***************')
    yield
    logger.info('*************** 結束執行測項 ***************')


def pytest_collection_modifyitems(items):
    for item in items:
        if 'test_case_setup_and_teardown' not in item.fixturenames:
            item.fixturenames.append('test_case_setup_and_teardown')

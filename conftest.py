import logging
import platform
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any, AsyncIterator, Type, TypeVar

import allure
import pytest
import pytest_asyncio
import requests

from api.user import UserAPI
from utils.api_provider import ApiClientProvider
from utils.async_base_ws import AsyncBaseWS
from utils.config_loader import get_config, load_test_config

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


def _create_user_helper(user_api: UserAPI, user_key: str):
    """從設定檔建立一個使用者。"""
    secrets = get_config()
    user_config = secrets.get('users', {}).get(user_key)
    if not user_config:
        logging.info(f"\nWarning: 在 secrets.yml 中找不到 user key '{user_key}'，跳過建立。")
        return

    account = user_config['account']
    password = user_config['password']
    logging.info(f"\nSetting up user '{account}' (from key: {user_key})...")

    result = user_api.register(account, password)

    if result.get('code') == 0:
        logging.info(f"User '{account}' created successfully.")
    elif result.get('code') == 2001:
        logging.info(f"User '{account}' already exists.")
    else:
        logging.info(f"An error occurred during setup for user '{account}': {result}")


@pytest.fixture(scope='session', autouse=True)
def setup_default_user(user_api: UserAPI):
    """
    在所有測試開始前，自動建立預設的通用測試帳號。
    """
    logging.info('開始建立預設帳號...')
    _create_user_helper(user_api, 'default_user')


@pytest.fixture(scope='session')
def setup_change_password_user(user_api: UserAPI):
    """
    為變更密碼測試建立專用帳號，需要在測試中明確引用。
    """
    _create_user_helper(user_api, 'change_password_user')


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
def api_provider(api_factory, shared_used_urls) -> ApiClientProvider:
    """提供 ApiClientProvider 實例，直接從全域設定獲取 URLs。"""
    env_urls = get_config().get('urls', {})
    return ApiClientProvider(api_factory, env_urls, shared_used_urls)


# --- 便利 API Fixtures ---


@pytest.fixture(scope='session')
def user_api(api_provider: ApiClientProvider) -> UserAPI:
    return api_provider.get(UserAPI)


# --- 登入輔助函式 ---


def _perform_pre_login(api_client: UserAPI, user_data: dict, token_prefix: str = ''):
    account, password = user_data['account'], user_data['password']
    with allure.step(f'前置步驟 => {account} 登入'):
        result = api_client.login(account, password)
        if result.get('status_code') != 200:
            raise ValueError(f'pre_login 失敗 Account:{account} \n{result}')
        token = result.get('data', {}).get('access_token')
        if not token:
            raise ValueError(f'登入 response 不含 token: {result}')
        api_client.session.headers['Authorization'] = f'{token_prefix}{token}'
        api_client.login_result = result


@pytest.fixture
def user_data(request: pytest.FixtureRequest) -> dict:
    """ 
    根據 parametrize 或預設值提供使用者資料。
    - 如果案例使用 parametrize (indirect=True)，則使用傳入的參數。
    - 參數可以是 string (在 secrets.yml 中的 user key)。
    - 參數可以是 dict (直接使用該使用者資料)。
    - 否則，回傳 'default_user' 的資料。
    """
    if hasattr(request, 'param'):
        param = request.param
        users = get_config()['users']

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

    default_user = get_config().get('users', {}).get('default_user')
    if not default_user:
        pytest.fail("在 secrets.yml 的 'users' 中找不到預設的 'default_user'")

    return default_user


# --- 預登入 Fixtures ---
@pytest.fixture
def pre_login(user_data: dict, user_api: UserAPI) -> Generator[UserAPI, None, None]:
    _perform_pre_login(user_api, user_data, token_prefix='Bearer ')
    yield user_api


@pytest_asyncio.fixture()
async def ws_connect(user_data: dict, user_api: UserAPI) -> AsyncIterator[AsyncBaseWS]:
    result = user_api.login(user_data['account'], user_data['password'])
    ws_url = result['data']['ws_url']
    with allure.step('WS connect'):
        ws = AsyncBaseWS(ws_url)
        await ws.connect()
    yield ws
    await ws.close_connect()


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
    logging.info('*************** 開始執行測項 ***************')
    yield
    logging.info('*************** 結束執行測項 ***************')


def pytest_collection_modifyitems(items):
    for item in items:
        if 'test_case_setup_and_teardown' not in item.fixturenames:
            item.fixturenames.append('test_case_setup_and_teardown')

import logging
from collections.abc import Generator
from typing import Any, AsyncIterator, Callable, TypedDict

import allure
import pytest
import pytest_asyncio
import requests

from api.auth import AuthAPI
from test_data.common.expectations import HTTP
from utils.api_provider import ApiClientProvider
from utils.async_base_ws import AsyncBaseWS

logger = logging.getLogger(__name__)


class UserDict(TypedDict):
    account: str
    password: str


# --- Core API Fixtures ---


@pytest.fixture(scope='package')
def shared_session() -> Generator[requests.Session, Any, None]:
    """提供一個在整個測試 package 中共用的 `requests.Session` 物件。

    Yields:
        一個 `requests.Session` 物件，用於共用連線。
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope='package')
def api_provider(shared_session: requests.Session, shared_used_urls: set, test_config: dict) -> ApiClientProvider:
    """提供一個 package 等級、已設定好的 API Client 提供者。

    組裝 `ApiClientProvider` 所需的所有依賴，包含共用的 `requests.Session`、
    從設定檔讀取的 URLS，以及用於 Allure 報告的 `shared_used_urls` 集合。
    此 fixture 作為所有 API 測試的統一入口，確保所有 API Client 都透過一致的方式建立和管理。

    Args:
        shared_session: 整個測試 package 中共用的 `requests.Session` 物件。
        shared_used_urls: 用於記錄所有被呼叫過的 URL 的集合，以產生 Allure 報告。
        test_config: 已根據環境 (--env) 讀取並解析的設定檔內容。

    Returns:
        一個已完全設定好、可供使用的 ApiClientProvider 物件。
    """
    # Note: shared_used_urls and test_config are from the root conftest.py
    env_urls = test_config.get('urls', {})
    return ApiClientProvider(shared_session, env_urls, shared_used_urls)


@pytest.fixture(scope='package')
def auth_api(api_provider: ApiClientProvider) -> AuthAPI:
    """提供一個 package 範圍的 `AuthAPI` 物件。

    Args:
        api_provider: API Client 的中心服務提供者。

    Returns:
        一個 `AuthAPI` 物件。
    """
    return api_provider.get(AuthAPI)


@pytest.fixture
def user_data(request: pytest.FixtureRequest, test_config: dict) -> UserDict:
    """根據測試參數或預設值，提供使用者資料。

    預設使用 `default_user`，可透過 indirect parametrize 覆寫，支援兩種形態：

        # 指定 secrets.yml 中的 user key
        @pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)

        # 直接給定帳密 (值須在 collection 階段即可決定)
        @pytest.mark.parametrize('user_data', [{'account': 'a', 'password': 'p'}], indirect=True)

    Args:
        request: pytest 的 request 物件，用於取得 indirect parametrize 傳入的參數。
        test_config: 包含所有使用者設定的字典。

    Returns:
        一個包含使用者帳號密碼的字典。

    Raises:
        pytest.fail: 如果設定檔中找不到指定的 user key。
    """
    param = getattr(request, 'param', 'default_user')
    if isinstance(param, dict):
        return param

    user = test_config.get('users', {}).get(param)
    if not user:
        pytest.fail(f"在 secrets.yml 的 'users' 中找不到 user key: '{param}'")
    return user


# --- Pre-login & Connection Fixtures ---


@pytest.fixture
def access_token(user_data: UserDict, auth_api: AuthAPI) -> str:
    """為測試案例預先登入，並回傳取得的 access token。

    Args:
        user_data: 使用者的帳號密碼資料。
        auth_api: 用於執行登入的 `AuthAPI` 物件。

    Returns:
        登入成功後取得的 access token (不含 'Bearer ' 前綴)。

    Raises:
        ValueError: 如果登入失敗或回傳結果中沒有 token。
    """
    account, password = user_data['account'], user_data['password']
    with allure.step(f'前置步驟 => {account} 登入'):
        result = auth_api.login(account, password)
        if result.get('status_code') != 200:
            raise ValueError(f'前置登入失敗 Account:{account} \n{result}')
        token = result.get('data', {}).get('access_token')
        if not token:
            raise ValueError(f'登入 response 不含 token: {result}')
    return token


@pytest.fixture
def authed_api(api_provider: ApiClientProvider, access_token: str) -> ApiClientProvider:
    """提供一個「已認證」的 API Client 來源。

    從此 Provider 取得的所有 client 都會自動帶上 Authorization header，
    因此測試中看到 `authed_api.get(SomeAPI)` 即可知道該 client 已具備授權。
    匿名的 `api_provider` 不受影響，登入、註冊等不該帶 token 的測試仍應使用它。

    Args:
        api_provider: 匿名的 API Client 提供者。
        access_token: 前置登入取得的 access token。

    Returns:
        一個已帶認證身分的 ApiClientProvider。
    """
    return api_provider.with_auth(access_token)


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


# --- User Creation Fixtures (Original content) ---


@pytest.fixture(scope='package')
def user_creator(auth_api: AuthAPI, test_config: dict) -> Callable[[str], None]:
    """提供一個用於建立測試使用者的工廠函式。

    將建立使用者所需的 `auth_api` 和 `test_config` 依賴包裝起來，
    回傳一個更簡單的函式，方便在各個 setup fixture 中重複使用。

    依賴的 `auth_api` 和 `test_config` fixture 來自於根 conftest.py。
    """

    def _creator(user_key: str):
        user_config = test_config.get('users', {}).get(user_key)
        if not user_config:
            logger.warning(f"\nWarning: 在 secrets.yml 中找不到 user key '{user_key}'，跳過建立。\n")
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


@pytest.fixture(scope='package', autouse=True)
def setup_default_user(user_creator: Callable[[str], None]):
    """在測試開始前，自動為 API 測試建立預設的測試帳號。"""
    logger.info('開始為 API 測試建立預設帳號...')
    user_creator('default_user')


@pytest.fixture(scope='package')
def setup_change_password_user(user_creator: Callable[[str], None]):
    """為密碼變更測試，建立專用的測試帳號。"""
    user_creator('change_password_user')


@pytest.fixture(scope='package')
def setup_duplicate_phone_user(user_creator: Callable[[str], None]):
    """為手機綁定測試，建立專用的測試帳號。"""
    user_creator('duplicate_phone_user')

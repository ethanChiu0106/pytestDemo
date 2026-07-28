import logging
from collections.abc import Generator
from typing import Any, AsyncIterator, Callable

import allure
import pytest
import pytest_asyncio
import requests

from api.auth import AuthAPI
from test_data.common.expectations import HTTP
from utils.api_provider import ApiClientProvider
from utils.async_base_ws import AsyncBaseWS
from utils.config_loader import User, get_config

logger = logging.getLogger(__name__)


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
def api_provider(shared_session: requests.Session, shared_used_urls: set) -> ApiClientProvider:
    """提供一個 package 等級、已設定好的 API Client 提供者。

    組裝 `ApiClientProvider` 所需的所有依賴，包含共用的 `requests.Session`、
    當前環境的設定，以及用於 Allure 報告的 `shared_used_urls` 集合。
    此 fixture 作為所有 API 測試的統一入口，確保所有 API Client 都透過一致的方式建立和管理。

    Args:
        shared_session: 整個測試 package 中共用的 `requests.Session` 物件。
        shared_used_urls: 用於記錄所有被呼叫過的 URL 的集合，以產生 Allure 報告 (來自根 conftest.py)。

    Returns:
        一個已完全設定好、可供使用的 ApiClientProvider 物件。
    """
    return ApiClientProvider(shared_session, get_config(), shared_used_urls)


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
def user_data(request: pytest.FixtureRequest) -> User:
    """根據測試參數或預設值，提供使用者資料。

    預設使用 `default_user`，可透過 indirect parametrize 覆寫，支援兩種形態：

        # 指定 secrets.yml 中的 user key
        @pytest.mark.parametrize('user_data', ['change_password_user'], indirect=True)

        # 直接給定帳密 (值須在 collection 階段即可決定)
        @pytest.mark.parametrize('user_data', [{'account': 'a', 'password': 'p'}], indirect=True)

    Args:
        request: pytest 的 request 物件，用於取得 indirect parametrize 傳入的參數。

    Returns:
        一個 `User` 物件。

    Raises:
        ConfigError: 如果設定檔中找不到指定的 user key。
    """
    param = getattr(request, 'param', 'default_user')
    if isinstance(param, dict):
        return User(**param)
    return get_config().user(param)


# --- Pre-login & Connection Fixtures ---


@pytest.fixture
def access_token(user_data: User, auth_api: AuthAPI) -> str:
    """為測試案例預先登入，並回傳取得的 access token。

    Args:
        user_data: 使用者的帳號密碼資料。
        auth_api: 用於執行登入的 `AuthAPI` 物件。

    Returns:
        登入成功後取得的 access token (不含 'Bearer ' 前綴)。

    Raises:
        ValueError: 如果登入失敗或回傳結果中沒有 token。
    """
    account, password = user_data.account, user_data.password
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
async def ws_connect(auth_api: AuthAPI, user_data: User) -> AsyncIterator[AsyncBaseWS]:
    """提供一個已連線的 WebSocket 物件。

    Args:
        auth_api: 用於登入以獲取 WebSocket URL 的 `AuthAPI` 物件。
        user_data: 登入所需的使用者資料。

    Yields:
        一個已連線的 `AsyncBaseWS` 物件。

    Raises:
        ValueError: 如果登入後找不到 WebSocket URL。
    """
    result = auth_api.login(user_data.account, user_data.password)
    async with AsyncBaseWS(auth_api.ws_url_from(result)) as ws:
        yield ws


# --- User Creation Fixtures ---


@pytest.fixture(scope='package')
def user_creator(auth_api: AuthAPI) -> Callable[[str], None]:
    """提供一個用於建立測試使用者的工廠函式。

    將建立使用者所需的 `auth_api` 依賴包裝起來，
    回傳一個更簡單的函式，方便在各個 setup fixture 中重複使用。

    找不到 user key 時只記錄警告並跳過，不讓建帳號這個前置動作使測試失敗
    (該使用者若真的被測試用到，屆時會由 `Config.user()` 明確報錯)。
    """

    def _creator(user_key: str):
        user = get_config().users.get(user_key)
        if not user:
            logger.warning(f"\nWarning: 在 secrets.yml 中找不到 user key '{user_key}'，跳過建立。\n")
            return

        account, password = user.account, user.password
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

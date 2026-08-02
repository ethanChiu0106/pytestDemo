from typing import Type, TypeVar

import requests

from api.service_names import Service
from utils.config_loader import Config

T = TypeVar('T')


class ApiClientProvider:
    """管理並提供所有 API Client 物件。

    它如同一個服務路由器，能根據需求，動態選擇設定檔中的 URL 來建立 API Client。
    """

    def __init__(
        self,
        session: requests.Session,
        config: Config,
        default_headers: dict = None,
    ):
        """初始化 Provider

        Args:
            session: 共用的 requests.Session 物件。
            config: 當前環境的測試設定，用於查詢各服務的 base URL。
            default_headers: 由此 Provider 建立的 client 都會帶上的 headers。
                用於表達 Provider 的身分 (例如已認證)，見 `with_auth`。
        """
        self._session = session
        self._config = config
        self._default_headers = default_headers or {}

    def with_auth(self, token: str) -> 'ApiClientProvider':
        """以指定的 token 建立一個「已認證」的 Provider。

        回傳的是新的 Provider 實例，原本的 Provider 不受影響，因此匿名與已認證
        兩種身分可以並存 (也可同時持有多個不同使用者的 Provider)。
        新舊 Provider 共用同一個 session。

        Args:
            token: 登入取得的 access token (不含 'Bearer ' 前綴)。

        Returns:
            一個新的、每次請求都會帶上 Authorization header 的 ApiClientProvider。
        """
        return ApiClientProvider(
            self._session,
            self._config,
            default_headers={**self._default_headers, 'Authorization': f'Bearer {token}'},
        )

    def _create_client(self, api_class: Type[T], base_url: str) -> T:
        """內部使用的 client 建立方法。"""
        return api_class(base_url=base_url, session=self._session, default_headers=self._default_headers)

    def get(self, api_class: Type[T], service: Service = None) -> T:
        """獲取一個設定好的 API Client 物件。

        服務的判定順序為: `service` 參數 > API class 的 `service` 屬性。
        兩者皆未提供時會直接拋錯，而非猜測一個預設服務。

        Args:
            api_class: 要建立的 API Client 類別。
            service: 指定要連線的服務，未提供時改用 api_class 的 `service` 屬性。

        Returns:
            一個已設定好 base_url、session 與身分的 API Client 物件。

        Raises:
            AttributeError: 如果 api_class 未宣告 `service` 屬性且未傳入 `service` 參數。
            ConfigError: 如果設定檔的 'urls' 中找不到該服務。
        """
        target_service = service or getattr(api_class, 'service', None)
        if target_service is None:
            raise AttributeError(
                f"{api_class.__name__} 未宣告 'service' 屬性，也未傳入 service 參數，無法決定要連線的服務"
            )

        base_url = self._config.url(target_service.value)

        return self._create_client(api_class, base_url)

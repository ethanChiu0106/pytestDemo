from typing import Type, TypeVar

import requests

T = TypeVar('T')


class ApiClientProvider:
    """管理並提供所有 API Client 物件。

    它如同一個服務路由器，能根據需求，動態選擇設定檔中的 URL 來建立 API Client。
    """

    def __init__(self, session: requests.Session, env_config: dict, used_urls_set: set):
        """初始化 Provider

        Args:
            session: 共用的 requests.Session 物件。
            env_config: 包含所有伺服器網址的字典 (來自設定檔的 'urls' 區塊)。
            used_urls_set: 共用的集合，用於記錄所有呼叫過的伺服器網址。
        """
        self._session = session
        self._env_config = env_config
        self._used_urls = used_urls_set

    def _create_client(self, api_class: Type[T], base_url: str) -> T:
        """內部使用的 client 建立方法。"""
        return api_class(base_url=base_url, session=self._session)

    def get(self, api_class: Type[T], service: str = None) -> T:
        """獲取一個設定好的 API Client 物件。"""
        service_name = service or getattr(api_class, 'service', 'back')

        if service_name not in self._env_config:
            raise KeyError(f"在 secrets.yml 的 'urls' 配置中，找不到服務 '{service_name}' 的 URL")

        base_url = self._env_config[service_name]
        self._used_urls.add(base_url)

        return self._create_client(api_class, base_url)

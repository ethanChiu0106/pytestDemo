from typing import Callable, Type, TypeVar

T = TypeVar('T')


class ApiClientProvider:
    """管理並提供所有 API Client 物件。

    主要工作是為測試案例準備好與正確伺服器溝通的 API Client
    會自動從設定檔讀取伺服器網址，並追蹤測試中使用過的網址
    """

    def __init__(self, api_factory: Callable, env_config: dict, used_urls_set: set):
        """初始化 Provider

        Args:
            api_factory: 用於建立 API Client 物件的函式
            env_config: 包含所有伺服器網址的字典
            used_urls_set: 共用的集合，用於記錄所有呼叫過的伺服器網址
        """
        self._api_factory = api_factory
        self._env_config = env_config
        self._used_urls = used_urls_set

    def get(self, api_class: Type[T], service: str = None) -> T:
        """獲取一個設定好的 API Client 物件

        提供需要的 API 類別 (例如 `AuthAPI`)，即回傳可直接使用的物件

        Args:
            api_class: 欲建立的 API Client 類別
            service: API 所屬服務 (例如 'back', 'app')，用來決定伺服器網址

        Returns:
            一個已設定好、可直接使用的 API Client 物件

        Raises:
            KeyError: 若在設定檔找不到對應網址，將引發此錯誤
        """
        service_name = service or getattr(api_class, 'service', 'back')

        if service_name not in self._env_config:
            raise KeyError(f"在 secrets.yml 的 'urls' 配置中，找不到服務 '{service_name}' 的 URL")

        base_url = self._env_config[service_name]
        self._used_urls.add(base_url)
        return self._api_factory(api_class, base_url)

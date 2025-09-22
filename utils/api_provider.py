from typing import Callable, Type, TypeVar

T = TypeVar('T')


class ApiClientProvider:
    """
    一個 API Client 提供者，可以根據需求即時建立指向正確環境的 API Client。
    同時會追蹤哪些 URL 在測試過程中被使用。
    """

    def __init__(self, api_factory: Callable, env_config: dict, used_urls_set: set):
        self._api_factory = api_factory
        self._env_config = env_config
        self._used_urls = used_urls_set  # 使用共享的 URL 集合

    def get(self, api_class: Type[T], service: str = None) -> T:
        """
        取得一個設定好的 API Client 實例。

        Args:
            api_class: 想要建立的 API Client 的類別 (例如 PermissionAPI)。
            service: 該 API 屬於哪個服務，對應 secrets.yml 中的鍵 (例如 'back', 'app')。
                    如果未提供，將嘗試從 api_class 的 'service' 屬性中獲取。

        Returns:
            一個設定好 base_url 的 API Client 實例。
        """
        service_name = service or getattr(api_class, 'service', 'back')

        if service_name not in self._env_config:
            raise KeyError(f"在 secrets.yml 中，找不到 '{service_name}' URL")

        base_url = self._env_config[service_name]
        self._used_urls.add(base_url)  # 追蹤此 URL
        return self._api_factory(api_class, base_url)

"""定義 API client 可路由的服務

`ApiClientProvider` 依 API class 宣告的 `service` 決定 base URL，此 Enum 界定可宣告的範圍。

`secrets.yml` 的 `urls` 底下除了這些服務，還有 UI 站台等不經過 Provider 的項目
(UI 走 `base_url` fixture)，因此這個 Enum 是 `urls` 的子集，而非它的完整鏡像。
"""

from enum import Enum


class Service(Enum):
    """定義所有 API 服務的名稱"""

    FRONT = 'front'
    BACK = 'back'

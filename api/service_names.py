"""定義服務名稱的 Enum

將 `secrets.yml` 設定檔中 `urls` 底下的服務名稱統一定義在此，避免在程式碼中直接使用字串，以提高可維護性。
"""

from enum import Enum


class Service(Enum):
    """定義所有 API 服務的名稱"""

    FRONT = 'front'
    BACK = 'back'

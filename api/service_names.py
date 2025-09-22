from enum import Enum


class Service(Enum):
    """
    定義所有 API 服務的名稱，方便統一管理和調用。
    """

    FRONT = 'front'
    BACK = 'back'

"""定義 WebSocket 通訊協定中使用的所有常數

主要包含操作碼 (op_code) 和不同業務流程的子操作碼 (sub_code)
"""

from enum import Enum


class OpCode(Enum):
    """定義 WebSocket 的主要操作碼 (OpCode)"""

    C2SPing = 1
    S2CPong = 2
    C2SPlayerFlow = 3
    S2CPlayerFlow = 4
    C2SItemFlow = 5
    S2CItemFlow = 6


class PlayerFlow(Enum):
    """定義玩家相關流程的 sub_code"""

    GetPlayerInfo = 1
    UpdateName = 2
    BindPhone = 3


class ItemFlow(Enum):
    """定義物品相關流程的sub_code"""

    GetAllItems = 1
    GetItemById = 2

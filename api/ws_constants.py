from enum import Enum


# @dataclass
class OpCode(Enum):
    C2SPing = 1
    S2CPong = 2
    C2SPlayerFlow = 3
    S2CPlayerFlow = 4
    C2SItemFlow = 5
    S2CItemFlow = 6


class C2SPlayerFlow(Enum):
    GetPlayerInfo = 1
    UpdateName = 2
    BindPhone = 3


class C2SItemFlow(Enum):
    GetAllItems = 1
    GetItemById = 2
    CreateItem = 3

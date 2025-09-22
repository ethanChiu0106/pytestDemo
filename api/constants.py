from enum import Enum


# @dataclass
class OpCode(Enum):
    C2SPing = 1
    S2CPong = 2
    C2SPlayerFlow = 3
    S2CPlayerFlow = 4


class C2SPlayerFlow(Enum):
    GetPlayerInfo = 1
    UpdateName = 2

from api.common import Common
from api.constants import OpCode


class Ping(Common):
    def __init__(self) -> None:
        super().__init__()
        self.op_code = OpCode.C2SPing.value

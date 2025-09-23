from api.common import Common
from api.constants import C2SPlayerFlow, OpCode
from utils.async_base_ws import AsyncBaseWS


class Player(Common):
    def __init__(self, ws_obj: AsyncBaseWS) -> None:
        super().__init__()
        self.ws = ws_obj
        self.op_code = OpCode.C2SPlayerFlow.value

    async def _send_player_flow_request(self, flow_type: C2SPlayerFlow, data: dict = None) -> dict:
        """
        私有輔助方法，用於處理所有 C2SPlayerFlow 相關的請求。
        """
        c2s_data = self.c2s_data(flow_type.value, data=data)
        result = await self.ws.send_and_receive(c2s_data, expected_op_code=OpCode.S2CPlayerFlow.value)
        return result

    async def get_player_info(self) -> dict:
        return await self._send_player_flow_request(C2SPlayerFlow.GetPlayerInfo)

    async def update_name(self, name: str) -> dict:
        data = {'name': name}
        return await self._send_player_flow_request(C2SPlayerFlow.UpdateName, data=data)

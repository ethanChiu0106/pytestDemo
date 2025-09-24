from api.constants import C2SPlayerFlow, OpCode
from utils.async_base_ws import AsyncBaseWS


class Player:
    def __init__(self, ws_obj: AsyncBaseWS) -> None:
        self.ws = ws_obj
        self.op_code = OpCode.C2SPlayerFlow.value

    async def _send_player_flow_request(self, flow_type: C2SPlayerFlow, data: dict = None) -> dict:
        """
        私有輔助方法，用於處理所有 C2SPlayerFlow 相關的請求。
        """
        result = await self.ws.send_and_receive(
            op_code=self.op_code,
            sub_code=flow_type.value,
            data=data,
            expected_op_code=OpCode.S2CPlayerFlow.value
        )
        return result

    async def get_player_info(self) -> dict:
        return await self._send_player_flow_request(C2SPlayerFlow.GetPlayerInfo)

    async def update_name(self, name: str) -> dict:
        data = {'name': name}
        return await self._send_player_flow_request(C2SPlayerFlow.UpdateName, data=data)

    async def update_phone(self, phone: str) -> dict:
        data = {'phone': phone}
        return await self._send_player_flow_request(C2SPlayerFlow.BindPhone, data=data)
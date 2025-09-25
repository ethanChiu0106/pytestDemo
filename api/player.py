from api.base_ws_api import BaseWsApi
from api.ws_constants import C2SPlayerFlow, OpCode


class Player(BaseWsApi):
    @property
    def op_code(self) -> int:
        return OpCode.C2SPlayerFlow.value

    @property
    def expected_op_code(self) -> int:
        return OpCode.S2CPlayerFlow.value

    async def get_player_info(self) -> dict:
        return await self._send_request(C2SPlayerFlow.GetPlayerInfo)

    async def update_name(self, name: str) -> dict:
        data = {'name': name}
        return await self._send_request(C2SPlayerFlow.UpdateName, data=data)

    async def update_phone(self, phone: str) -> dict:
        data = {'phone': phone}
        return await self._send_request(C2SPlayerFlow.BindPhone, data=data)

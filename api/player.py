from api.base_ws_api import BaseWsApi
from api.ws_constants import PlayerFlow, OpCode


class PlayerWS(BaseWsApi):
    @property
    def op_code(self) -> int:
        return OpCode.C2SPlayerFlow.value

    @property
    def expected_op_code(self) -> int:
        return OpCode.S2CPlayerFlow.value

    async def get_player_info(self) -> dict:
        return await self._send_request(PlayerFlow.GetPlayerInfo)

    async def update_name(self, name: str) -> dict:
        data = {'name': name}
        return await self._send_request(PlayerFlow.UpdateName, data=data)

    async def bind_phone(self, telephone: str) -> dict:
        data = {'telephone': telephone}
        return await self._send_request(PlayerFlow.BindPhone, data=data)

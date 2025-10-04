from api.base_ws_api import BaseWsApi
from api.ws_constants import OpCode, PlayerFlow


class PlayerWS(BaseWsApi):
    """提供玩家資訊相關的 WebSocket API"""

    @property
    def op_code(self) -> int:
        return OpCode.C2SPlayerFlow.value

    @property
    def expected_op_code(self) -> int:
        return OpCode.S2CPlayerFlow.value

    async def get_player_info(self) -> dict:
        """透過 WebSocket 獲取玩家資訊

        Returns:
            一個包含 API 回應結果的 dict
        """
        return await self._send_request(PlayerFlow.GetPlayerInfo)

    async def update_name(self, name: str) -> dict:
        """透過 WebSocket 更新玩家名稱

        Args:
            name: 新的玩家名稱

        Returns:
            一個包含 API 回應結果的 dict
        """
        data = {'name': name}
        return await self._send_request(PlayerFlow.UpdateName, data=data)

    async def bind_phone(self, telephone: str) -> dict:
        """透過 WebSocket 綁定玩家手機號碼

        Args:
            telephone: 要綁定的手機號碼

        Returns:
            一個包含 API 回應結果的 dict
        """
        data = {'telephone': telephone}
        return await self._send_request(PlayerFlow.BindPhone, data=data)

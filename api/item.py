from api.service_names import Service
from utils.base_request import BaseRequest

from .base_ws_api import BaseWsApi
from .ws_constants import ItemFlow, OpCode


class ItemAPI(BaseRequest):
    """提供物品相關的 HTTP API"""

    service = Service.FRONT.value

    def __init__(self, base_url: str, session=None):
        """初始化 ItemAPI

        Args:
            base_url: API 的 base URL
            session: 共用的 `requests.Session` 物件，可選
        """
        super().__init__(base_url, session=session)

    def get_all_items(self) -> dict:
        result = self.get('/items/')
        return result

    def get_item(self, item_id: int) -> dict:
        result = self.get(f'/items/{item_id}')
        return result


class ItemWS(BaseWsApi):
    """提供物品相關的 WebSocket API"""

    @property
    def op_code(self) -> int:
        return OpCode.C2SItemFlow.value

    @property
    def expected_op_code(self) -> int:
        return OpCode.S2CItemFlow.value

    async def get_item_by_id(self, item_id: int) -> dict:
        data = {'item_id': item_id}
        return await self._send_request(sub_code=ItemFlow.GetItemById, data=data)

    async def get_all_items(self) -> dict:
        return await self._send_request(sub_code=ItemFlow.GetAllItems)

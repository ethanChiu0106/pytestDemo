from api.service_names import Service
from utils.base_request import BaseRequest

from .base_ws_api import BaseWsApi
from .ws_constants import ItemFlow, OpCode


class ItemAPI(BaseRequest):
    service = Service.FRONT.value

    def __init__(self, base_url: str, session=None):
        super().__init__(base_url, session=session)

    def get_items(self) -> dict:
        """
        Retrieves a list of all items.
        """
        result = self.get('/items/')
        return result

    def get_item(self, item_id: int) -> dict:
        """
        Retrieves a single item by its ID.
        """
        result = self.get(f'/items/{item_id}')
        return result


class ItemWS(BaseWsApi):
    @property
    def op_code(self) -> int:
        return OpCode.C2SItemFlow.value

    @property
    def expected_op_code(self) -> int:
        return OpCode.S2CItemFlow.value

    async def get_item_by_id(self, item_id: dict) -> dict:
        """透過 WebSocket 獲取單一物品"""
        data = {'item_id': item_id}
        return await self._send_request(sub_code=ItemFlow.GetItemById, data=data)

    async def get_all_items(self) -> dict:
        """透過 WebSocket 獲取所有物品"""
        return await self._send_request(sub_code=ItemFlow.GetAllItems)

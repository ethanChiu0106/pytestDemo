from api.service_names import Service
from utils.base_request import BaseRequest


class ItemAPI(BaseRequest):
    """
    API client for interacting with the Item resource.
    """
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

    def create_item(self, name: str, description: str | None = None) -> dict:
        """
        Creates a new item.
        """
        json_data = {'name': name}
        if description is not None:
            json_data['description'] = description
        result = self.post('/items/', json=json_data)
        return result

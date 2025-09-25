from api.service_names import Service
from utils.base_request import BaseRequest


class AuthAPI(BaseRequest):
    service = Service.FRONT.value

    def __init__(self, base_url: str, session=None):
        super().__init__(base_url, session=session)
        self.login_result: dict | None = None

    def register(self, account: str, password: str) -> dict:
        """
        帳號5~20英數
        密碼7~20英數
        """
        json_data = {'account': account, 'password': password}
        result = self.post('/auth/register', json=json_data)
        return result

    def login(self, account: str, password: str) -> dict:
        json_data = {'account': account, 'password': password}
        result = self.post('/auth/login', json=json_data)
        return result

    def change_password(self, old_password: str, new_password: str) -> dict:
        json_data = {'old_password': old_password, 'new_password': new_password}
        result = self.put('/user/password', json=json_data)
        return result

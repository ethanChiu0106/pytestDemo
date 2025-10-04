from api.service_names import Service
from utils.base_request import BaseRequest


class AuthAPI(BaseRequest):
    """提供使用者認證 (註冊、登入、變更密碼) 相關的 API。"""

    service = Service.FRONT.value

    def __init__(self, base_url: str, session=None):
        """初始化 AuthAPI

        Args:
            base_url: API 的 base URL
            session: 共用的 `requests.Session` 物件，可選
        """
        super().__init__(base_url, session=session)
        self.login_result: dict | None = None

    def register(self, account: str, password: str) -> dict:
        """註冊帳號

        Args:
            account: 使用者帳號 (5~20英數字元)
            password: 使用者密碼 (7~20英數字元)

        Returns:
            一個包含 API 回應結果的字典
        """
        json_data = {'account': account, 'password': password}
        result = self.post('/auth/register', json=json_data)
        return result

    def login(self, account: str, password: str) -> dict:
        """使用帳號密碼登入

        Args:
            account: 使用者帳號
            password: 使用者密碼

        Returns:
            一個包含 API 回應結果的字典，成功時應包含 token
        """
        json_data = {'account': account, 'password': password}
        result = self.post('/auth/login', json=json_data)
        return result

    def change_password(self, old_password: str, new_password: str) -> dict:
        """變更已登入使用者的密碼

        呼叫此 API 前，必須先登入並將 token 設定在 session header 中
        """
        json_data = {'old_password': old_password, 'new_password': new_password}
        result = self.put('/user/password', json=json_data)
        return result

from api.service_names import Service
from utils.base_request import BaseRequest


class AuthAPI(BaseRequest):
    """提供使用者認證 (註冊、登入、變更密碼) 相關的 API。"""

    service = Service.FRONT

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

        此 API 需要授權，請透過 `ApiClientProvider.with_auth()` 取得帶認證的 client 再呼叫
        (測試中可直接使用 `authed_api` fixture)。
        """
        json_data = {'old_password': old_password, 'new_password': new_password}
        result = self.put('/user/password', json=json_data)
        return result

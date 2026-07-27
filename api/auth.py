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

    @staticmethod
    def ws_url_from(login_result: dict) -> str:
        """從登入回應取出 WebSocket 的連線位址

        WebSocket 的位址由登入回應提供，因此需要授權的 WS 操作都得先登入。
        此處是這段解構的唯一出處，登入回應的形狀若有變動只需改這裡。

        Args:
            login_result: `login` 回傳的結果。

        Returns:
            WebSocket 的連線位址。

        Raises:
            ValueError: 如果回應中找不到 'ws_url'
        """
        ws_url = login_result.get('data', {}).get('ws_url')
        if not ws_url:
            raise ValueError(f"登入成功，但在 Response 中找不到 'ws_url': {login_result}")
        return ws_url

    def change_password(self, old_password: str, new_password: str) -> dict:
        """變更已登入使用者的密碼

        此 API 需要授權，請透過 `ApiClientProvider.with_auth()` 取得帶認證的 client 再呼叫
        (測試中可直接使用 `authed_api` fixture)。
        """
        json_data = {'old_password': old_password, 'new_password': new_password}
        result = self.put('/user/password', json=json_data)
        return result

"""
存放測試相關的預期結果。
"""


def _http_expectation(code: int, status_code: int) -> dict:
    """建立 HTTP 預期結果"""
    return {'code': code, 'status_code': status_code}


def _ws_error_expectation(error_code: int) -> dict:
    """建立 WebSocket 錯誤預期結果"""
    return {'error_code': error_code, 'success': False}


class Common:
    """通用預期結果"""

    SUCCESS = _http_expectation(0, 200)
    FAIL_HTTP_STRUCTURE = {'code': None, 'status_code': None, 'msg': None}


class Auth:
    """使用者驗證相關功能的預期結果"""

    class Validation:
        """通用的驗證相關錯誤"""

        ACCOUNT_FORMAT_ERROR = _http_expectation(2001, 400)
        PASSWORD_FORMAT_ERROR = _http_expectation(2003, 400)

    class Register:
        """註冊相關"""

        SUCCESS = _http_expectation(0, 201)
        REPEATED_ACCOUNT = _http_expectation(2000, 400)

    class Login:
        """登入相關"""

        ACCOUNT_ERROR = _http_expectation(2002, 400)
        PASSWORD_ERROR = _http_expectation(2004, 400)


class Item:
    """物品相關功能的預期結果 (REST)"""

    class GetItem:
        """獲取物品相關"""

        NOT_FOUND = _http_expectation(3010, 404)


class WebSocket:
    """WebSocket 相關功能的預期結果"""

    SUCCESS = {'success': True}
    UNSUPPORTED_SUBCODE = _ws_error_expectation(3002)
    UNSUPPORTED_OPCODE = _ws_error_expectation(3004)
    INTERNAL_SERVER_ERROR = _ws_error_expectation(3005)

    class User:
        """使用者相關"""

        USER_NOT_FOUND = _ws_error_expectation(3000)
        NEW_NAME_NOT_PROVIDED = _ws_error_expectation(3001)
        USER_FROM_TOKEN_NOT_FOUND = _ws_error_expectation(3003)
        TELEPHONE_NOT_PROVIDED = _ws_error_expectation(3006)
        INVALID_TELEPHONE_FORMAT = _ws_error_expectation(3007)
        TELEPHONE_ALREADY_REGISTERED = _ws_error_expectation(3008)
        INVALID_USERNAME_FORMAT = _ws_error_expectation(3013)

    class Item:
        """物品相關"""

        ITEM_ID_NOT_PROVIDED = _ws_error_expectation(3009)
        ITEM_NOT_FOUND = _ws_error_expectation(3010)
        ITEM_DATA_NOT_PROVIDED = _ws_error_expectation(3011)
        INVALID_ITEM_DATA = _ws_error_expectation(3012)

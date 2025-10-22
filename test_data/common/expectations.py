"""
存放測試相關的預期結果。
"""


def _http_expectation(code: int, status_code: int) -> dict:
    """建立 HTTP 預期結果"""
    return {'code': code, 'status_code': status_code}


def _ws_error_expectation(error_code: int) -> dict:
    """建立 WebSocket 錯誤預期結果"""
    return {'error_code': error_code, 'success': False}


def _ui_expectation(success: bool, error_message: str | None) -> dict:
    """建立 UI 預期結果"""
    return {'success': success, 'error_message': error_message}


class HTTP:
    """包含所有 HTTP 相關的預期結果"""

    class Common:
        """通用預期結果"""

        SUCCESS = _http_expectation(0, 200)
        FAIL_HTTP_STRUCTURE = {'code': int, 'status_code': int, 'msg': str}

        class Schemas:
            """通用的 Schema 結構"""

            SUCCESS_WITH_NULL_DATA = {'status_code': int, 'code': int, 'data': None}

    class Auth:
        """使用者驗證相關功能的預期結果"""

        class Schemas:
            """Auth 相關的 Schema 結構"""

            LOGIN_SUCCESS = {
                'code': int,
                'data': {
                    'access_token': str,
                    'ws_url': str,
                    'player_info': {'username': str, 'telephone': (type(None), str)},
                },
            }
            REGISTER_SUCCESS = {
                'status_code': int,
                'code': int,
                'data': {'account': str, 'username': str, 'telephone': None, 'id': int},
            }

        class Validation:
            ACCOUNT_FORMAT_ERROR = _http_expectation(2001, 400)
            PASSWORD_FORMAT_ERROR = _http_expectation(2003, 400)

        class Register:
            SUCCESS = _http_expectation(0, 201)
            REPEATED_ACCOUNT = _http_expectation(2000, 400)

        class Login:
            ACCOUNT_ERROR = _http_expectation(2002, 400)
            PASSWORD_ERROR = _http_expectation(2004, 400)

    class Item:
        """物品相關功能的預期結果 (REST)"""

        class Schemas:
            """Item 相關的 Schema 結構"""

            GET_SINGLE_ITEM = {'status_code': int, 'code': int, 'data': {'name': str, 'description': str, 'id': int}}
            GET_ITEM_LIST = {'status_code': int, 'code': int, 'data': [{'name': str, 'description': str, 'id': int}]}

        class GetItem:
            NOT_FOUND = _http_expectation(3010, 404)


class WebSocket:
    """WebSocket 相關功能的預期結果"""

    class Schemas:
        """WebSocket 相關的 Schema 結構"""

        PLAYER_INFO = {
            'success': bool,
            'op_code': int,
            'data': {'username': str, 'telephone': (type(None), str)},
            'error_code': int,
            'error_msg': str,
            'sub_code': int,
        }
        SINGLE_ITEM = {
            'success': bool,
            'op_code': int,
            'data': {'name': str, 'description': str, 'id': int},
            'error_code': int,
            'error_msg': str,
            'sub_code': int,
        }
        ITEM_LIST = {
            'success': bool,
            'op_code': int,
            'data': [{'name': str, 'description': str, 'id': int}],
            'error_code': int,
            'error_msg': str,
            'sub_code': int,
        }
        FAIL = {
            'success': bool,
            'op_code': int,
            'data': None,
            'error_code': int,
            'error_msg': str,
            'sub_code': int,
        }

    class Common:
        """通用的 WebSocket 預期結果"""

        SUCCESS = {'success': True, 'error_code': 0, 'error_msg': ''}

    class User:
        TELEPHONE_NOT_PROVIDED = _ws_error_expectation(3006)
        INVALID_TELEPHONE_FORMAT = _ws_error_expectation(3007)
        TELEPHONE_ALREADY_REGISTERED = _ws_error_expectation(3008)
        INVALID_USERNAME_FORMAT = _ws_error_expectation(3013)

    class Item:
        ITEM_ID_NOT_PROVIDED = _ws_error_expectation(3009)
        ITEM_NOT_FOUND = _ws_error_expectation(3010)


class UI:
    """包含所有 UI 相關的預期結果"""

    INVENTORY_URL_REGEX = '.*inventory.html'

    class Login:
        """登入頁面相關的預期結果"""

        SUCCESS = _ui_expectation(True, None)
        LOGIN_FAIL = _ui_expectation(False, 'Epic sadface: Username and password do not match any user in this service')
        EMPTY_USERNAME = _ui_expectation(False, 'Epic sadface: Username is required')
        EMPTY_PASSWORD = _ui_expectation(False, 'Epic sadface: Password is required')

    class Purchase:
        """購買流程相關的預期結果和常量"""

        # Product
        PURCHASE_QUANTITY = '1'

        # URL Reg
        CART_URL_REGEX = '.*cart.html'
        CHECKOUT_STEP_ONE_URL_REGEX = '.*checkout-step-one.html'
        CHECKOUT_STEP_TWO_URL_REGEX = '.*checkout-step-two.html'
        CHECKOUT_COMPLETE_URL_REGEX = '.*checkout-complete.html'

"""存放測試預期結果的可重用零件。

此處的常數多半是 `Expectation` 的其中一格，而非完整的 `Expectation`：

    expected={'result': HTTP.Common.SUCCESS, 'schema': HTTP.Auth.Schemas.LOGIN_SUCCESS}

`Schemas` 底下是填進 `schema` 的結構，其餘是填進 `result` 的值。
UI 的常數是例外，UI 不經過 `verify_case_auto`，存的是完整的預期結果。

各形狀的型別定義在 `base.py`。頁面網址不在此處，屬於各 Page Object 的屬性。
"""

from .base import UILoginExpectation

# 物品的欄位結構，HTTP 與 WebSocket 兩種協定回傳的形狀相同
_ITEM_FIELDS = {'name': str, 'description': str, 'id': int}


def _http_schema(data_schema) -> dict:
    """建立 HTTP 回應的 schema，外層固定，只有 data 依 API 而不同"""
    return {'status_code': int, 'code': int, 'data': data_schema}


def _ws_schema(data_schema) -> dict:
    """建立 WebSocket 回應的 schema，外層固定，只有 data 依 API 而不同"""
    return {
        'success': bool,
        'op_code': int,
        'data': data_schema,
        'error_code': int,
        'error_msg': str,
        'sub_code': int,
    }


class HTTP:
    """包含所有 HTTP 相關的預期結果"""

    class Common:
        """通用預期結果"""

        SUCCESS = {'code': 0, 'status_code': 200}

        class Schemas:
            """通用的 Schema 結構"""

            SUCCESS_WITH_NULL_DATA = _http_schema(None)
            FAIL = {'code': int, 'status_code': int, 'msg': str}

    class Auth:
        """使用者驗證相關功能的預期結果"""

        class Schemas:
            """Auth 相關的 Schema 結構"""

            LOGIN_SUCCESS = _http_schema(
                {
                    'access_token': str,
                    'ws_url': str,
                    'player_info': {'username': str, 'telephone': (type(None), str)},
                }
            )
            REGISTER_SUCCESS = _http_schema({'account': str, 'username': str, 'telephone': None, 'id': int})

        class Validation:
            """欄位格式驗證的預期結果"""

            ACCOUNT_FORMAT_ERROR = {'code': 2001, 'status_code': 400}
            PASSWORD_FORMAT_ERROR = {'code': 2003, 'status_code': 400}

        class Register:
            """註冊功能的預期結果"""

            SUCCESS = {'code': 0, 'status_code': 201}
            REPEATED_ACCOUNT = {'code': 2000, 'status_code': 400}

        class Login:
            """登入功能的預期結果"""

            ACCOUNT_ERROR = {'code': 2002, 'status_code': 400}
            PASSWORD_ERROR = {'code': 2004, 'status_code': 400}

    class Item:
        """物品相關功能的預期結果 (REST)"""

        class Schemas:
            """Item 相關的 Schema 結構"""

            GET_SINGLE_ITEM = _http_schema(_ITEM_FIELDS)
            GET_ITEM_LIST = _http_schema([_ITEM_FIELDS])

        class GetItem:
            """獲取單一物品的預期結果"""

            NOT_FOUND = {'code': 3010, 'status_code': 404}


class WebSocket:
    """WebSocket 相關功能的預期結果"""

    class Schemas:
        """WebSocket 相關的 Schema 結構"""

        PLAYER_INFO = _ws_schema({'username': str, 'telephone': (type(None), str)})
        SINGLE_ITEM = _ws_schema(_ITEM_FIELDS)
        ITEM_LIST = _ws_schema([_ITEM_FIELDS])
        FAIL = _ws_schema(None)

    class Common:
        """通用的 WebSocket 預期結果"""

        SUCCESS = {'success': True, 'error_code': 0, 'error_msg': ''}

    class User:
        """使用者相關功能的預期結果"""

        TELEPHONE_NOT_PROVIDED = {'error_code': 3006, 'success': False}
        INVALID_TELEPHONE_FORMAT = {'error_code': 3007, 'success': False}
        TELEPHONE_ALREADY_REGISTERED = {'error_code': 3008, 'success': False}
        INVALID_USERNAME_FORMAT = {'error_code': 3013, 'success': False}

    class Item:
        """物品相關功能的預期結果"""

        ITEM_ID_NOT_PROVIDED = {'error_code': 3009, 'success': False}
        ITEM_NOT_FOUND = {'error_code': 3010, 'success': False}


class UI:
    """包含所有 UI 相關的預期結果"""

    class Login:
        """登入頁面相關的預期結果"""

        SUCCESS: UILoginExpectation = {'success': True, 'error_message': None}
        LOGIN_FAIL: UILoginExpectation = {
            'success': False,
            'error_message': 'Epic sadface: Username and password do not match any user in this service',
        }
        EMPTY_USERNAME: UILoginExpectation = {
            'success': False,
            'error_message': 'Epic sadface: Username is required',
        }
        EMPTY_PASSWORD: UILoginExpectation = {
            'success': False,
            'error_message': 'Epic sadface: Password is required',
        }

"""
存放 Auth 模組相關測試的預期結果。
"""

# 成功的預期結果
SUCCESS_EXPECTED = {
    'code': 0,
    'status_code': 200,
}

WS_SUCCESS_EXPECTED = {'success': True}

REGISTER_SUCCESS_EXPECTED = {
    'code': 0,
    'status_code': 201,
}

# 帳號已重複的預期結果
REPEATED_ACCOUNT_EXPECTED = {
    'code': 2000,
    'status_code': 400,
}

# 帳號格式錯誤的預期結果
ACCOUNT_FORMAT_ERROR_EXPECTED = {
    'code': 2001,
    'status_code': 400,
}
PASSWORD_FORMAT_ERROR_EXPECTED = {
    'code': 2003,
    'status_code': 400,
}
# 登入失敗：帳號錯誤
LOGIN_ACCOUNT_ERROR_EXPECTED = {
    'code': 2002,
    'status_code': 400,
}

# 登入失敗：密碼錯誤
LOGIN_PASSWORD_ERROR_EXPECTED = {
    'code': 2004,
    'status_code': 400,
}

"""
存放測試資料生成等共享的輔助函式。
"""

import random
from enum import Enum

from faker import Faker

fake = Faker('zh_TW')


def generate_accounts(num, min_len=5, max_len=20):
    """
    產生指定數量的英數字帳號。
    """
    accounts = []
    for _ in range(num):
        random_length = random.randint(min_len, max_len)
        account = fake.password(
            length=random_length, special_chars=False, digits=True, upper_case=True, lower_case=True
        )
        accounts.append(account)
    return accounts


def create_ws_expectation(base_expectation: dict, op_code_enum: Enum, sub_code_enum: Enum) -> dict:
    """
    以基礎預期結果為範本，建立包含 op_code 和 sub_code 的 WS 預期。

    Args:
        base_expectation: 基礎預期結果，如 WebSocket.Common.SUCCESS 或 WebSocket.User.TELEPHONE_NOT_PROVIDED
        op_code_enum: OpCode 的 enum 成員
        sub_code_enum: 對應的 sub_code enum 成員
    Returns:
        包含 op_code 和 sub_code 的完整預期字典
    """
    expectation = base_expectation.copy()
    expectation['op_code'] = op_code_enum.value
    expectation['sub_code'] = sub_code_enum.value
    return expectation

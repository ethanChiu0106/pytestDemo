"""
存放測試資料生成等共享的輔助函式。
"""

import random
from enum import Enum

import allure
import pytest
from faker import Faker

from .base import AllureCase, CombinedTestCase
from .enums import PytestMark

# 初始化 Faker
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


def create_param_from_case(case: CombinedTestCase, id: str = None) -> pytest.param:
    """
    將一個測試案例的 dataclass 物件轉換為 pytest.param 物件，
    並使用型別安全的 Enum 動態地附加 pytest 和 allure 的標籤。
    """
    all_marks = []

    # --- 處理 Pytest 標籤 ---
    if hasattr(case, 'marks') and case.marks:
        # 這個字典將 PytestMark Enum 映射到實際的 pytest.mark 物件
        marks_map = {
            PytestMark.SKIP: pytest.mark.skip,
            PytestMark.WS: pytest.mark.ws,
            PytestMark.POSITIVE: pytest.mark.positive,
            PytestMark.NEGATIVE: pytest.mark.negative,
            PytestMark.SINGLE: pytest.mark.single,
        }
        for mark_enum in case.marks:
            mark_obj = marks_map.get(mark_enum)
            if mark_obj:
                all_marks.append(mark_obj)

    # --- 處理 Allure 標籤 ---
    if isinstance(case, AllureCase):
        # 處理標準的 allure 標籤，如 story, feature 等
        allure_tags_map = {
            'parent_suite': allure.parent_suite,
            'suite': allure.suite,
            'sub_suite': allure.sub_suite,
            'epic': allure.epic,
            'feature': allure.feature,
            'story': allure.story,
        }
        for key, allure_marker in allure_tags_map.items():
            value = getattr(case, key, None)
            if value:
                all_marks.append(allure_marker(value))

        if hasattr(case, 'severity') and case.severity:
            all_marks.append(allure.severity(case.severity.value))

    # 使用案例的 title 或提供的 id 作為測試案例的 ID
    case_id = id or getattr(case, 'title', 'N/A')

    return pytest.param(case, marks=all_marks, id=case_id)


def create_ws_expectation(base_expectation: dict, op_code_enum: Enum, sub_code_enum: Enum) -> dict:
    """
    以基礎預期結果為範本，建立包含 op_code 和 sub_code 的 WS 預期。
    :param base_expectation: 基礎預期結果，如 WebSocket.Common.SUCCESS 或 WebSocket.User.TELEPHONE_NOT_PROVIDED
    :param op_code_enum: OpCode 的 enum 成員
    :param sub_code_enum: 對應的 sub_code enum 成員
    :return: 包含 op_code 和 sub_code 的完整預期字典
    """
    expectation = base_expectation.copy()
    expectation['op_code'] = op_code_enum.value
    expectation['sub_code'] = sub_code_enum.value
    return expectation

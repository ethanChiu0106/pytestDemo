"""
存放 auth 子套件中共享的輔助函式。
"""

import random

import allure
import pytest
from faker import Faker

from .base import AllureCase, CombinedTestCase
from .enums import AllureSeverity, PytestMark

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
    Converts a test case dataclass object into a pytest.param object,
    dynamically attaching pytest and allure marks using type-safe enums.
    """
    all_marks = []

    # --- Process Pytest Marks ---
    if hasattr(case, 'marks') and case.marks:
        # This map links the PytestMark enum to the actual pytest.mark object.
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

    # --- Process Allure Marks ---
    if isinstance(case, AllureCase):
        # Handle standard allure tags like story, feature, etc.
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

        # Convert our custom AllureSeverity enum to the official allure.severity_level
        if hasattr(case, 'severity') and case.severity:
            severity_map = {
                AllureSeverity.BLOCKER: allure.severity_level.BLOCKER,
                AllureSeverity.CRITICAL: allure.severity_level.CRITICAL,
                AllureSeverity.NORMAL: allure.severity_level.NORMAL,
                AllureSeverity.MINOR: allure.severity_level.MINOR,
                AllureSeverity.TRIVIAL: allure.severity_level.TRIVIAL,
            }
            allure_severity_level = severity_map.get(case.severity)
            if allure_severity_level:
                all_marks.append(allure.severity(allure_severity_level))

    # Use the case's title or the provided id for the test case ID
    case_id = id or getattr(case, 'title', 'N/A')

    return pytest.param(case, marks=all_marks, id=case_id)

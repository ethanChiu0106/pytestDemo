from enum import Enum

import allure


class PytestMark(Enum):
    """
    定義所有可用的 Pytest mark。
    使用 Enum 可以確保型別安全並提供自動完成功能。
    """

    WS = 'ws'
    HTTP = 'http'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    SINGLE = 'single'
    SCENARIO = 'scenario'
    UI_SINGLE = 'ui_single'
    UI_SCENARIO = 'ui_scenario'
    SKIP = 'skip'


class AllureSeverity(Enum):
    """
    定義所有可用的 Allure 嚴重級別。
    其值直接對應 allure.severity_level，以提供型別安全和集中管理。
    """

    BLOCKER = allure.severity_level.BLOCKER
    CRITICAL = allure.severity_level.CRITICAL
    NORMAL = allure.severity_level.NORMAL
    MINOR = allure.severity_level.MINOR
    TRIVIAL = allure.severity_level.TRIVIAL

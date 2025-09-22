from enum import Enum


class PytestMark(Enum):
    """
    Defines all available Pytest marks.
    Using an Enum ensures type safety and provides auto-completion.
    """

    WS = 'ws'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    SINGLE = 'single'
    SKIP = 'skip'


class AllureSeverity(Enum):
    """
    Defines all available Allure severity levels.
    This provides a layer of abstraction and type safety for test case definitions.
    """

    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    MINOR = 'minor'
    TRIVIAL = 'trivial'

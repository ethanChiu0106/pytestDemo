from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Protocol, TypeVar


from .enums import AllureSeverity, PytestMark

# A generic type variable representing the structure of the Request
RequestType = TypeVar('RequestType')


@dataclass
class TestCaseData(Generic[RequestType]):
    """Core data for a test case (request, expected, etc.)"""

    request: Optional[RequestType]
    expected: Dict[str, Any]
    marks: List[PytestMark]


@dataclass
class AllureCase:
    """Base test case, including classification tags for Allure reports"""

    # Fields without default values must come first.
    title: str
    description: str
    sub_suite: str
    story: str
    parent_suite: str
    suite: str
    epic: str
    feature: str

    # Fields with default values must come last.
    severity: AllureSeverity = AllureSeverity.NORMAL  # Use the new custom enum


class CombinedTestCase(Protocol[RequestType]):
    """
    A Protocol defining the combined interface expected by create_param_from_case.
    This allows for more precise type hinting when a case object inherits from multiple base classes.
    """

    request: Optional[RequestType]
    expected: Dict[str, Any]
    marks: List[PytestMark]
    title: str
    description: str
    parent_suite: str
    suite: str
    sub_suite: str
    epic: str
    feature: str
    story: str
    severity: AllureSeverity

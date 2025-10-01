"""
產生與「獲取多個物品」功能相關的測試資料。
"""

from dataclasses import dataclass

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import Common
from test_data.common.helpers import create_param_from_case


@dataclass
class GetItemsRequest:
    """獲取多個物品 API 的請求資料 (此API不需要參數)"""

    pass


@dataclass
class GetItemsCase(AllureCase, TestCaseData[GetItemsRequest]):
    """獲取多個物品 API 的測試案例"""

    parent_suite: str = 'HTTP API 測試'
    suite: str = '物品'
    epic: str = '物品相關功能'
    feature: str = '獲取多個物品'


def generate_get_items_cases() -> list:
    """
    產生獲取多個物品 API 的測試情境。
    """
    cases = [
        create_param_from_case(
            GetItemsCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 成功獲取所有物品',
                sub_suite='獲取多個物品 - 成功',
                title='成功獲取所有物品列表',
                description='測試是否能成功獲取所有物品的列表',
                request=GetItemsRequest(),
                expected={
                    'result': Common.SUCCESS,
                    'schema': {
                        'status_code': None,
                        'code': None,
                        'data': [{'name': None, 'description': None, 'id': None}],
                    },
                },
                marks=[PytestMark.POSITIVE, PytestMark.HTTP, PytestMark.SINGLE],
            ),
            id='get_items_success',
        ),
    ]
    return cases

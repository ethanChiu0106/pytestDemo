"""
產生與「物品」功能相關的測試資料。
"""

from dataclasses import dataclass

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.expectations import Common, Item
from test_data.common.helpers import create_param_from_case


@dataclass
class GetItemRequest:
    """獲取物品 API 的請求資料"""

    item_id: int


@dataclass
class GetItemCase(AllureCase, TestCaseData[GetItemRequest]):
    """獲取物品 API 的測試案例"""

    parent_suite: str = 'HTTP API 測試'
    suite: str = '物品'
    epic: str = '物品相關功能'
    feature: str = '獲取物品'


def generate_get_item_cases() -> list:
    """
    產生獲取物品 API 的測試情境。
    """
    cases = [
        create_param_from_case(
            GetItemCase(
                severity=AllureSeverity.NORMAL,
                story='正向情境 - 成功獲取物品',
                sub_suite='獲取物品 - 成功',
                title='獲取存在的物品',
                description='使用 item_id=1 測試是否能成功獲取物品',
                request=GetItemRequest(item_id=1),
                expected={
                    'result': Common.SUCCESS,
                    'schema': {
                        'status_code': None,
                        'code': None,
                        'data': {'name': None, 'description': None, 'id': None},
                    },
                },
                marks=[PytestMark.POSITIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='get_item_success',
        ),
        create_param_from_case(
            GetItemCase(
                severity=AllureSeverity.NORMAL,
                story='反向情境 - 物品不存在',
                sub_suite='獲取物品 - 失敗',
                title='獲取不存在的物品',
                description='使用一個極大的 item_id 測試物品不存在的情境',
                request=GetItemRequest(item_id=999999),
                expected={'result': Item.GetItem.NOT_FOUND, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='get_item_not_found',
        ),
        create_param_from_case(
            GetItemCase(
                severity=AllureSeverity.NORMAL,
                story='邊界值情境 - 無效的 item_id',
                sub_suite='獲取物品 - 失敗',
                title='使用 item_id=0',
                description='使用 item_id=0 測試邊界值',
                request=GetItemRequest(item_id=0),
                expected={'result': Item.GetItem.NOT_FOUND, 'schema': Common.FAIL_HTTP_STRUCTURE},
                marks=[PytestMark.NEGATIVE, PytestMark.SINGLE, PytestMark.HTTP],
            ),
            id='get_item_with_id_zero',
        ),
    ]
    return cases

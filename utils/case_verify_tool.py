"""提供通用於測試案例的自訂斷言工具"""

import logging
from typing import Any, Dict

import allure

logger = logging.getLogger(__name__)


@allure.step('驗證 test data expected value')
def assert_result(actual_result: Dict[str, Any], expected_result: Dict[str, Any]):
    """比對實際結果與預期結果的字典

    此函式只會比對 `expected_result` 中存在的鍵值對
    這允許在不同環境下，即使 API 回應的欄位不完全相同，也能進行核心欄位的驗證

    Args:
        actual_result: 實際的 API 回應字典
        expected_result: 預期的結果字典

    Raises:
        AssertionError: 如果 `actual_result` 中缺少 `expected_result` 的任何鍵，
                        或者共同鍵的值不匹配
    """
    # 結構驗證：確保所有預期的鍵都存在於實際結果中
    expected_keys = set(expected_result.keys())
    actual_keys = set(actual_result.keys())

    if not expected_keys.issubset(actual_keys):
        missing_keys = expected_keys - actual_keys
        error_msg = f'驗證失敗：實際結果中缺少預期的鍵 (Missing keys in actual result): {missing_keys}'
        logger.error(error_msg)
        assert False, error_msg

    # 內容驗證：只比對共同存在的鍵
    common_keys = expected_keys
    filtered_actual = {key: actual_result[key] for key in common_keys}
    filtered_expected = {key: expected_result[key] for key in common_keys}

    if filtered_actual != filtered_expected:
        logger.error(
            f'比對失敗！\n實際結果 (僅比對共同欄位): {filtered_actual}\n預期結果 (僅比對共同欄位): {filtered_expected}'
        )

    # 再次斷言，以便觸發 Pytest 的詳細 diff 報告
    assert filtered_actual == filtered_expected


@allure.step('驗證回應的巢狀結構 (Nested Structure)')
def assert_structure(actual_dict: dict, expected_schema: dict):
    """遞迴驗證一個字典是否符合預期的巢狀結構

    Args:
        actual_dict: 要檢查的字典 (例如 API 回應)
        expected_schema: 描述預期結構的字典。其格式支援：
            - 萬用字元: `'key': None` (只檢查鍵存在)
            - 型別: `'key': int`
            - 多重型別: `'key': (int, str, type(None))`
            - 巢狀物件: `'key': {'sub_key': str}`
            - 物件列表: `'key': [{'id': int}]`
            - 純值列表: `'key': [int]`

    Raises:
        AssertionError: 如果結構或型別不匹配
        TypeError: 如果 `expected_schema` 本身的格式不合法
    """

    def _verify_list(path: str, data_list: list, schema_list: list):
        """輔助函式：專門驗證列表"""
        assert isinstance(data_list, list), f"路徑 '{path}' 的值應為列表，但實際是 {type(data_list)}"
        if not schema_list:
            return  # 如果 schema 是 `[]`，僅驗證是列表即可

        item_schema = schema_list[0]
        for i, item in enumerate(data_list):
            _verify_value(f'{path}[{i}]', item, item_schema)

    def _verify_value(path: str, data: Any, schema: Any):
        """輔助函式：根據 schema 型別分派驗證邏輯"""
        if schema is None:
            return

        if isinstance(schema, tuple):
            assert isinstance(data, schema), f"路徑 '{path}' 的值型別 {type(data)} 不在預期的型別元組 {schema} 中"
        elif isinstance(schema, dict):
            assert isinstance(data, dict), f"路徑 '{path}' 的值應為字典，但實際是 {type(data)}"
            assert_structure(data, schema)
        elif isinstance(schema, list):
            _verify_list(path, data, schema)
        elif isinstance(schema, type):
            assert isinstance(data, schema), f"路徑 '{path}' 的值應為 {schema} 型別，但實際是 {type(data)}"
        else:
            raise TypeError(f"預期結構 (schema) 中 '{path}' 的值 '{schema}' 不是合法的型別、字典、列表、元組或 None")

    assert isinstance(actual_dict, dict), f'要驗證的對象不是字典，而是 {type(actual_dict)}'

    expected_keys = set(expected_schema.keys())
    actual_keys = set(actual_dict.keys())
    assert expected_keys.issubset(actual_keys), f'回應中缺少 key(s): {expected_keys - actual_keys}'

    for key, sub_schema in expected_schema.items():
        _verify_value(key, actual_dict[key], sub_schema)


def verify_case_auto(actual_result: Dict[str, Any], expected: Dict[str, Any]):
    """根據預期資料的結構，自動選擇斷言方法

    - 如果 `expected` 包含 'schema' 鍵，則進行結構驗證。
    - 如果 `expected` 包含 'result' 鍵，則進行值驗證。
    - 如果兩者都沒，則將 `expected` 本身當作值來驗證。

    Args:
        actual_result: 實際的 API 回應。
        expected: 包含預期結果和/或結構的字典。
    """
    expected_schema = expected.get('schema')
    expected_result = expected.get('result')
    if expected_schema:
        assert_structure(actual_result, expected_schema)

    if expected_result:
        assert_result(actual_result, expected_result)
    else:
        expected_to_assert = {k: v for k, v in expected.items() if k != 'schema'}
        if expected_to_assert:
            assert_result(actual_result, expected_to_assert)

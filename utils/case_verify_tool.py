"""提供通用於測試案例的自訂斷言工具"""

import logging
from functools import singledispatch
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
            _verify_value(item_schema, f'{path}[{i}]', item)

    @singledispatch
    def _verify_value_dispatcher(schema: Any, path: str, verify_data: Any):
        """預設的處理器，處理所有未被明確註冊的型別"""
        raise TypeError(f"預期結構 (schema) 中 '{path}' 的值 '{schema}' 不是合法的型別、字典、列表、元組或 None")

    @_verify_value_dispatcher.register(type(None))
    def _handle_none(schema, path, verify_data):
        """處理 schema 為 None 的情況"""
        return

    @_verify_value_dispatcher.register(tuple)
    def _handle_tuple(schema, path, verify_data):
        """處理 schema 為 tuple (多重型別) 的情況"""
        assert isinstance(verify_data, schema), (
            f"路徑 '{path}' 的值型別 {type(verify_data)} 不在預期的型別元組 {schema} 中"
        )

    @_verify_value_dispatcher.register(dict)
    def _handle_dict(schema, path, verify_data):
        """處理 schema 為 dict (巢狀物件) 的情況"""
        assert isinstance(verify_data, dict), f"路徑 '{path}' 的值應為字典，但實際是 {type(verify_data)}"
        assert_structure(verify_data, schema)

    @_verify_value_dispatcher.register(list)
    def _handle_list(schema, path, verify_data):
        """處理 schema 為 list (列表) 的情況"""
        _verify_list(path, verify_data, schema)

    @_verify_value_dispatcher.register(type)
    def _handle_type(schema, path, verify_data):
        """處理 schema 為 type (單一型別) 的情況"""
        assert isinstance(verify_data, schema), f"路徑 '{path}' 的值應為 {schema} 型別，但實際是 {type(verify_data)}"

    def _verify_value(schema: Any, path: str, verify_data: Any):
        """根據 schema 型別分派驗證邏輯"""
        _verify_value_dispatcher(schema, path, verify_data)

    assert isinstance(actual_dict, dict), f'要驗證的對象不是字典，而是 {type(actual_dict)}'

    expected_keys = set(expected_schema.keys())
    actual_keys = set(actual_dict.keys())
    assert expected_keys.issubset(actual_keys), f'回應中缺少 key(s): {expected_keys - actual_keys}'

    for key, sub_schema in expected_schema.items():
        _verify_value(sub_schema, key, actual_dict[key])


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

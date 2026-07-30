"""提供通用於測試案例的自訂斷言工具"""

import logging
from typing import Any, Dict

import allure

from test_data.common.base import Expectation

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
    missing_keys = expected_keys - set(actual_result.keys())

    if missing_keys:
        error_msg = f'驗證失敗：實際結果中缺少預期的鍵 (Missing keys in actual result): {missing_keys}'
        logger.error(error_msg)
        assert False, error_msg

    # 內容驗證：只取預期的鍵比對，讓斷言失敗時的 diff 不被無關欄位淹沒
    filtered_actual = {key: actual_result[key] for key in expected_keys}

    assert filtered_actual == expected_result


def _verify_value(schema: Any, path: str, value: Any):
    """依 schema 的形態驗證單一值

    Args:
        schema: 預期結構的片段，支援 None (略過)、型別、型別元組、dict (巢狀)、list。
        path: 此值在回應中的位置，僅用於錯誤訊息。
        value: 實際的值。

    Raises:
        AssertionError: 如果結構或型別不匹配
        TypeError: 如果 `schema` 本身的格式不合法
    """
    if schema is None:
        return
    if isinstance(schema, tuple):
        assert isinstance(value, schema), f"路徑 '{path}' 的值型別 {type(value)} 不在預期的型別元組 {schema} 中"
    elif isinstance(schema, dict):
        assert isinstance(value, dict), f"路徑 '{path}' 的值應為字典，但實際是 {type(value)}"
        assert_structure(value, schema)
    elif isinstance(schema, list):
        assert isinstance(value, list), f"路徑 '{path}' 的值應為列表，但實際是 {type(value)}"
        if schema:  # schema 為 `[]` 時僅驗證是列表
            for index, item in enumerate(value):
                _verify_value(schema[0], f'{path}[{index}]', item)
    elif isinstance(schema, type):
        assert isinstance(value, schema), f"路徑 '{path}' 的值應為 {schema} 型別，但實際是 {type(value)}"
    else:
        raise TypeError(f"預期結構 (schema) 中 '{path}' 的值 '{schema}' 不是合法的型別、字典、列表、元組或 None")


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
    assert isinstance(actual_dict, dict), f'要驗證的對象不是字典，而是 {type(actual_dict)}'

    expected_keys = set(expected_schema.keys())
    actual_keys = set(actual_dict.keys())
    assert expected_keys.issubset(actual_keys), f'回應中缺少 key(s): {expected_keys - actual_keys}'

    for key, sub_schema in expected_schema.items():
        _verify_value(sub_schema, key, actual_dict[key])


def verify_case_auto(actual_result: Dict[str, Any], expected: Expectation):
    """驗證 API 回應是否符合預期

    `schema` 為選填，提供時會先驗證回應的結構與型別；`result` 必填，用於比對欄位值。

    Args:
        actual_result: 實際的 API 回應。
        expected: 包含預期結果與 (選填的) 預期結構。
    """
    if expected_schema := expected.get('schema'):
        assert_structure(actual_result, expected_schema)

    assert_result(actual_result, expected['result'])

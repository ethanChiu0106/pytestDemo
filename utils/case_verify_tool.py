import logging
from typing import Any, Dict

import allure

logger = logging.getLogger(__name__)


@allure.step('驗證 test data expected value')
def assert_result(actual_result: Dict[str, Any], expected_result: Dict[str, Any]):
    """
    比對測試結果。
    1. 驗證所有 expected_result 中的鍵都存在於 actual_result 中。
    2. 僅比對 expected_result 和 actual_result 中【共同存在】的鍵的值。
    這允許在不同產品/環境下，即使回傳的欄位不完全相同，也能進行驗證。

    Args:
        actual_result (dict): 實際回傳結果。
        expected_result (dict): 預期結果。
    """
    # 步驟 1: 結構驗證 - 確保所有預期的鍵都存在於實際結果中
    expected_keys = set(expected_result.keys())
    actual_keys = set(actual_result.keys())

    if not expected_keys.issubset(actual_keys):
        missing_keys = expected_keys - actual_keys
        error_msg = f'驗證失敗：實際結果中缺少預期的鍵 (Missing keys in actual result): {missing_keys}'
        logger.error(error_msg)
        # 直接觸發斷言失敗，並顯示清晰的錯誤訊息
        assert False, error_msg

    # 步驟 2: 內容驗證 - 只從預期結果中存在的 key 來建立過濾後的字典，進行比對
    common_keys = expected_keys
    filtered_actual = {key: actual_result[key] for key in common_keys}
    filtered_expected = {key: expected_result[key] for key in common_keys}

    if filtered_actual != filtered_expected:
        logger.error(
            f'比對失敗！\n實際結果 (僅比對共同欄位): {filtered_actual}\n預期結果 (僅比對共同欄位): {filtered_expected}'
        )

    # 再次斷言，以便在主控台觸發 Pytest 的詳細 diff 報告
    assert filtered_actual == filtered_expected


@allure.step('驗證回應的巢狀結構 (Nested Structure)')
def assert_structure(actual_dict: dict, expected_schema: dict):
    """
    遞迴地驗證一個字典是否符合預期的巢狀結構。
    此版本經過重構，使用輔助函式與更清晰的命名以提高可讀性。

    :param actual_dict: 要檢查的字典 (例如 API 回應)。
    :param expected_schema: 一個描述預期結構的字典。
                            - 萬用字元: `'key': None` (只檢查鍵存在)
                            - 型別: `'key': int`
                            - 巢狀物件: `'key': {'sub_key': str}`
                            - 物件列表: `'key': [{'id': int}]`
                            - 純值列表: `'key': [int]`
    """

    def _verify_list(path: str, data_list: list, schema_list: list):
        """輔助函式：專門驗證列表。"""
        assert isinstance(data_list, list), f"路徑 '{path}' 的值應為列表，但實際是 {type(data_list)}"
        if not schema_list:
            return  # 如果 schema 是 `[]`，僅驗證是列表即可

        item_schema = schema_list[0]
        for i, item in enumerate(data_list):
            # 遞迴驗證列表中的每一個元素
            _verify_value(f'{path}[{i}]', item, item_schema)

    def _verify_value(path: str, data: Any, schema: Any):
        """輔助函式：根據 schema 型別分派驗證邏輯。"""
        # 如果 schema 為 None，視為萬用字元，不驗證型別或結構，直接通過
        if schema is None:
            return

        if isinstance(schema, dict):
            assert isinstance(data, dict), f"路徑 '{path}' 的值應為字典，但實際是 {type(data)}"
            # 遞迴主函式處理巢狀字典
            assert_structure(data, schema)
        elif isinstance(schema, list):
            _verify_list(path, data, schema)
        elif isinstance(schema, type):
            assert isinstance(data, schema), f"路徑 '{path}' 的值應為 {schema} 型別，但實際是 {type(data)}"
        else:
            raise TypeError(f"預期結構 (schema) 中 '{path}' 的值 '{schema}' 不是合法的型別、字典、列表或 None。")

    assert isinstance(actual_dict, dict), f'要驗證的對象不是字典，而是 {type(actual_dict)}'

    expected_keys = set(expected_schema.keys())
    actual_keys = set(actual_dict.keys())
    assert expected_keys.issubset(actual_keys), f'回應中缺少 key(s): {expected_keys - actual_keys}'

    for key, sub_schema in expected_schema.items():
        _verify_value(key, actual_dict[key], sub_schema)


def verify_case_auto(actual_result: Dict[str, Any], expected: Dict[str, Any]):
    """
    自動根據 expected 的結構進行驗證。

    - 如果 expected 包含 'schema' 鍵，則會使用 assert_structure 進行結構驗證。
    - 如果 expected 包含 'result' 鍵，則會使用 assert_result 進行值驗證。
    - 如果 'result' 鍵不存在，則會將 expected 中除了 'schema' 以外的所有鍵/值用於 assert_result 進行值驗證。

    Args:
        actual_result (Dict[str, Any]): 實際的 API 回應。
        expected (Dict[str, Any]): 包含預期結果和/或結構的字典。
    """
    expected_schema = expected.get('schema')
    expected_result = expected.get('result')
    if expected_schema:
        assert_structure(actual_result, expected_schema)

    if expected_result:
        assert_result(actual_result, expected_result)
    else:
        # 如果沒有 'result' key，就用除了 'schema' 之外的所有 key
        expected_to_assert = {k: v for k, v in expected.items() if k != 'schema'}
        # 只有在還有其他key時才進行斷言
        if expected_to_assert:
            assert_result(actual_result, expected_to_assert)

import logging
from typing import Any, Dict


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
        logging.error(error_msg)
        # 直接觸發斷言失敗，並顯示清晰的錯誤訊息
        assert False, error_msg

    # 步驟 2: 內容驗證 - 只從預期結果中存在的 key 來建立過濾後的字典，進行比對
    common_keys = expected_keys
    filtered_actual = {key: actual_result[key] for key in common_keys}
    filtered_expected = {key: expected_result[key] for key in common_keys}

    if filtered_actual != filtered_expected:
        logging.error(
            f'比對失敗！\n實際結果 (僅比對共同欄位): {filtered_actual}\n預期結果 (僅比對共同欄位): {filtered_expected}'
        )

    # 再次斷言，以便在主控台觸發 Pytest 的詳細 diff 報告
    assert filtered_actual == filtered_expected

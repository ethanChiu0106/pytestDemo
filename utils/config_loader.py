from collections.abc import Mapping

import pytest

from utils.read_data import ReadFileData

# 用於快取已載入設定的私有變數
_config_cache: dict | None = None


def deep_merge_dicts(base, override):
    """深度合併字典，用於合併 common 和特定環境的設定。"""
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, Mapping) and key in result and isinstance(result[key], Mapping):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def load_test_config(env: str) -> dict:
    """【共用函式】根據環境名稱，載入、合併並快取 secrets.yml 中的設定。"""
    global _config_cache
    # 如果已有快取，直接回傳，避免重複載入
    if _config_cache is not None:
        return _config_cache

    try:
        all_configs = ReadFileData.read_yaml_data('data', 'secrets.yml')
    except FileNotFoundError:
        config_path = 'data/secrets.yml'
        pytest.fail(f'設定檔 {config_path} 不存在。請先從 secrets.yml.template 複製一份並填入資料。')

    common_config = all_configs.get('common', {})
    env_specific_config = all_configs.get(env, {})
    final_config = deep_merge_dicts(common_config, env_specific_config)

    # 將載入的設定存入快取
    _config_cache = final_config
    return final_config


def get_config() -> dict:
    """
    取得由 load_test_config 載入並快取的設定。
    """
    if _config_cache is None:
        # 這個錯誤只會在 pytest 啟動流程不完整時發生
        raise RuntimeError('Config 尚未被載入，請確認您是透過 pytest 執行測試。')
    return _config_cache

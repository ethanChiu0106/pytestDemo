"""負責載入並管理專案的測試設定檔 (secrets.yml)"""

import functools
import logging
from collections.abc import Mapping
from pathlib import Path

import pytest
import yaml

# --- 模組級別變數 ---
_CURRENT_ENV: str | None = None
logger = logging.getLogger(__name__)
BASE_PATH = Path(__file__).resolve().parent.parent


# --- 公開函式 ---


def set_current_env(env: str):
    """設定當前測試要使用的環境 (由 conftest.py 呼叫)"""
    global _CURRENT_ENV
    _CURRENT_ENV = env


def get_config() -> dict:
    """取得已快取的設定

    此函式會呼叫內部被快取的讀取函式
    只有在第一次被呼叫時會真正讀取檔案，後續呼叫會立即回傳結果

    Returns:
        一個包含測試設定的字典

    Raises:
        RuntimeError: 如果環境尚未透過 `set_current_env` 設定
    """
    if _CURRENT_ENV is None:
        raise RuntimeError('測試環境尚未設定，請確認 pytest 啟動流程正確。')
    return _load_config_from_file(_CURRENT_ENV)


@functools.lru_cache
def _load_config_from_file(env: str) -> dict:
    """根據環境名稱，載入並合併設定 (此函式的結果會被快取)

    Args:
        env: 環境名稱 (例如 'qa', 'dev')

    Returns:
        一個包含最終合併設定的字典

    Raises:
        pytest.fail: 如果 `config/secrets.yml` 檔案不存在
    """
    config_dir = 'config'
    try:
        all_configs = _read_yaml(config_dir, 'secrets.yml')
    except FileNotFoundError:
        config_path = f'{config_dir}/secrets.yml'
        pytest.fail(f'設定檔 {config_path} 不存在。請先從 secrets.yml.template 複製一份並填入資料。')

    common_config = all_configs.get('common', {})
    env_specific_config = all_configs.get(env, {})
    final_config = deep_merge_dicts(common_config, env_specific_config)

    return final_config


def _read_yaml(directory: str, yaml_file_name: str) -> dict:
    """讀取並解析一個 YAML 檔案

    Args:
        directory: 目標檔案所在的目錄名稱 (相對於專案根目錄)
        yaml_file_name: 目標 YAML 檔案的名稱

    Returns:
        一個包含解析後 YAML 資料的字典
    """
    data_file_path = Path('/') / BASE_PATH / directory / yaml_file_name
    logger.info('讀取 %s 文件.....', yaml_file_name)
    with open(data_file_path, encoding='utf-8') as f:
        content = f.read()

    yaml_data = yaml.safe_load(content)

    logger.info('取得資料 => %s', yaml_data)
    return yaml_data


def deep_merge_dicts(base: dict, override: dict):
    """遞迴地深度合併兩個字典

    Args:
        base: 基礎字典
        override: 用於覆蓋的字典

    Returns:
        一個合併後的新字典
    """
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, Mapping) and key in result and isinstance(result[key], Mapping):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

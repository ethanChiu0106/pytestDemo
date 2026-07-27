"""負責載入並管理專案的測試設定檔 (secrets.yml)"""

import functools
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

_CURRENT_ENV: str | None = None
logger = logging.getLogger(__name__)
BASE_PATH = Path(__file__).resolve().parent.parent


class ConfigError(RuntimeError):
    """設定檔缺漏或格式不符"""


@dataclass(frozen=True)
class User:
    """secrets.yml 的 'users' 區塊中，一個測試使用者的資料

    Attributes:
        account: 登入帳號。
        password: 登入密碼。
        phone: 手機號碼，只有部分使用者有設定。
    """

    account: str
    password: str
    phone: str | None = None


@dataclass(frozen=True)
class Config:
    """單一環境 (--env) 的測試設定

    Attributes:
        env: 環境名稱，用於錯誤訊息指出是哪個環境缺設定。
        urls: 服務名稱到 base URL 的對應 (來自 'urls' 區塊)。
        users: user key 到 `User` 的對應 (來自 'users' 區塊)。
    """

    env: str
    urls: Mapping[str, str]
    users: Mapping[str, User]

    def user(self, key: str) -> User:
        """取得指定的測試使用者

        Args:
            key: secrets.yml 'users' 區塊中的 key。

        Returns:
            對應的 `User` 物件。

        Raises:
            ConfigError: 如果該環境的設定中找不到此 key。
        """
        if key not in self.users:
            raise ConfigError(
                f"環境 '{self.env}' 的 'users' 中找不到 '{key}'，可用的有: {sorted(self.users)}"
            )
        return self.users[key]

    def url(self, service: str) -> str:
        """取得指定服務的 base URL

        Args:
            service: 服務名稱 (例如 'front', 'back', 'ui')。

        Returns:
            該服務的 base URL。

        Raises:
            ConfigError: 如果該環境的設定中找不到此服務。
        """
        if service not in self.urls:
            raise ConfigError(
                f"環境 '{self.env}' 的 'urls' 中找不到服務 '{service}'，可用的有: {sorted(self.urls)}"
            )
        return self.urls[service]


def set_current_env(env: str):
    """設定當前測試要使用的環境 (由 conftest.py 呼叫)"""
    global _CURRENT_ENV
    _CURRENT_ENV = env


def get_config() -> Config:
    """取得已快取的設定

    此函式會呼叫內部被快取的讀取函式
    只有在第一次被呼叫時會真正讀取檔案，後續呼叫會立即回傳結果

    Returns:
        當前環境的 `Config` 物件。

    Raises:
        RuntimeError: 如果環境尚未透過 `set_current_env` 設定
    """
    if _CURRENT_ENV is None:
        raise RuntimeError('測試環境尚未設定，請確認 pytest 啟動流程正確。')
    return _load_config_from_file(_CURRENT_ENV)


@functools.lru_cache
def _load_config_from_file(env: str) -> Config:
    """根據環境名稱，載入並合併設定 (此函式的結果會被快取)

    Args:
        env: 環境名稱 (例如 'qa', 'dev')

    Returns:
        合併 `common` 與該環境設定後的 `Config` 物件。

    Raises:
        ConfigError: 如果 `config/secrets.yml` 不存在、格式不符，或缺少 'urls' / 'users' 區塊。
    """
    config_dir = 'config'
    config_path = f'{config_dir}/secrets.yml'
    try:
        all_configs = _read_yaml(config_dir, 'secrets.yml')
    except FileNotFoundError:
        raise ConfigError(f'設定檔 {config_path} 不存在。請先從 secrets.yml.template 複製一份並填入資料。')

    # 空檔或格式錯誤時 yaml.safe_load 會回 None，直接往下走會變成難以追查的 AttributeError。
    # CI 從 secret 寫入此檔，寫壞時要能一眼看出是設定檔的問題。
    if not isinstance(all_configs, Mapping):
        raise ConfigError(f'設定檔 {config_path} 格式不符，最外層應是 key-value 結構。')

    common_config = all_configs.get('common', {})
    env_specific_config = all_configs.get(env, {})
    final_config = deep_merge_dicts(common_config, env_specific_config)

    for section in ('urls', 'users'):
        if not isinstance(final_config.get(section), Mapping):
            raise ConfigError(f"環境 '{env}' 的設定中缺少 '{section}' 區塊。")

    users = {key: User(**value) for key, value in final_config['users'].items()}
    return Config(env=env, urls=final_config['urls'], users=users)


def _read_yaml(directory: str, yaml_file_name: str) -> dict:
    """讀取並解析一個 YAML 檔案

    Args:
        directory: 目標檔案所在的目錄名稱 (相對於專案根目錄)
        yaml_file_name: 目標 YAML 檔案的名稱

    Returns:
        一個包含解析後 YAML 資料的字典
    """
    data_file_path = BASE_PATH / directory / yaml_file_name
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

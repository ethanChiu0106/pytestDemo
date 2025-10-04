"""一個腳本，用於從 `secrets.yml` 產生一個已淨化的範本檔案。

此腳本會讀取 `config/secrets.yml`，將其中的所有值替換為
通用的佔位符 (例如 'your_string_value_here', 0)，然後將結果
寫入 `config/secrets.yml.template`。

這有助於保持範本檔案與實際設定檔的結構同步，同時避免洩漏敏感資訊。
"""
from pathlib import Path

import yaml


def sanitize_value(value):
    """根據值的類型，回傳一個對應的佔位符

    Args:
        value: 原始值。

    Returns:
        一個無敏感資訊的佔位符。
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return 'your_string_value_here'
    if isinstance(value, int):
        return 0
    if isinstance(value, float):
        return 0.0
    return None


def sanitize_dict_recursively(data):
    """遞迴地淨化一個字典，將所有值替換為佔位符

    Args:
        data: 要淨化的字典。

    Returns:
        一個所有值都已被替換為佔位符的新字典。
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict_recursively(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_value(item) for item in value]
        else:
            sanitized[key] = sanitize_value(value)
    return sanitized


def main():
    """執行腳本的主要邏輯

    讀取 `secrets.yml`，產生一個不含敏感資訊的範本檔案，
    並覆寫 `config/secrets.yml.template`。
    """
    project_root = Path(__file__).resolve().parent.parent
    config_dir = 'config'
    secrets_path = project_root / config_dir / 'secrets.yml'
    template_path = project_root / config_dir / 'secrets.yml.template'

    print(f'正在從 {secrets_path} 產生範本...')

    if not secrets_path.exists():
        print(f'錯誤: 找不到來源檔案 {secrets_path}。請確保您本地有此檔案。')
        return

    with open(secrets_path, 'r', encoding='utf-8') as f:
        real_data = yaml.safe_load(f)

    sanitized_data = sanitize_dict_recursively(real_data)

    with open(template_path, 'w', encoding='utf-8') as f:
        yaml.dump(sanitized_data, f, indent=2, allow_unicode=True)

    print(f'成功！範本檔案 {template_path} 已更新。')
    print('請記得將更新後的範本檔案加入您的 Git commit 中。')


if __name__ == '__main__':
    main()

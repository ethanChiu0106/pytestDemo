import yaml
from pathlib import Path

def sanitize_value(value):
    """根據值的類型回傳一個佔位符。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return "your_string_value_here"
    if isinstance(value, int):
        return 0
    if isinstance(value, float):
        return 0.0
    return None

def sanitize_dict_recursively(data):
    """遞迴地淨化一個字典。"""
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
    """
    讀取本地的 secrets.yml，產生一個不含敏感資訊的範本檔案
    並覆寫 data/secrets.yml.template。
    """
    project_root = Path(__file__).resolve().parent.parent
    secrets_path = project_root / 'data' / 'secrets.yml'
    template_path = project_root / 'data' / 'secrets.yml.template'

    print(f"正在從 {secrets_path} 產生範本...")

    if not secrets_path.exists():
        print(f"錯誤: 找不到來源檔案 {secrets_path}。請確保您本地有此檔案。")
        return

    with open(secrets_path, 'r', encoding='utf-8') as f:
        real_data = yaml.safe_load(f)

    sanitized_data = sanitize_dict_recursively(real_data)

    with open(template_path, 'w', encoding='utf-8') as f:
        yaml.dump(sanitized_data, f, indent=2, allow_unicode=True)
    
    print(f"成功！範本檔案 {template_path} 已更新。")
    print("請記得將更新後的範本檔案加入您的 Git commit 中。")

if __name__ == "__main__":
    main()

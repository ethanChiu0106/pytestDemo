import argparse
import logging
import random
import sys
from pathlib import Path

from faker import Faker

# ----------------- Path Setup -----------------
# 將專案根目錄加入到 Python 路徑中，以便引用其他模組
# 這是獨立腳本在大型專案中的常見模式
try:
    # 假設此腳本位於專案根目錄的子目錄中
    project_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_root))
except NameError:
    # 為互動式環境提供備用路徑
    project_root = Path('.').resolve()
    sys.path.append(str(project_root))

# 現在我們可以從專案模組中匯入
from api.user import UserAPI
from utils.read_data import ReadFileData

# ----------------- Configuration -----------------

# 初始化 Faker 用於產生隨機資料
fake = Faker('zh_TW')

# 設定基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)


# ----------------- Helper Functions -----------------


def register_account(user_api: UserAPI, account: str, password: str) -> bool:
    """
    註冊單一帳號並記錄結果。

    :param user_api: UserAPI 的實例。
    :param account: 要註冊的帳號名稱。
    :param password: 帳號的密碼。
    :return: 如果註冊成功返回 True，否則返回 False。
    """
    logging.info(f'嘗試註冊帳號: {account}')
    result = user_api.register(account, password)

    if result.get('status_code') == 200:
        logging.info(f'成功註冊帳號: {account}')
        print(f'成功註冊帳號: {account}, 密碼: {password}')
        return True
    else:
        error_message = result.get('err_msg', '未知錯誤')
        logging.error(f'註冊帳號失敗: {account}. 原因: {error_message}')
        return False


def generate_and_register_accounts(user_api: UserAPI, num_accounts: int):
    """
    產生並註冊指定數量的帳號。

    :param user_api: UserAPI 的實例。
    :param num_accounts: 要建立的帳號數量。
    """
    if num_accounts <= 0:
        logging.warning('帳號數量必須為正數。')
        return

    logging.info(f'開始為 {num_accounts} 個帳號進行批次註冊...')
    successful_registrations = 0
    for i in range(num_accounts):
        # 產生符合格式的隨機帳號和密碼
        account_length = random.randint(5, 20)
        new_account = fake.password(
            length=account_length, special_chars=False, upper_case=True, lower_case=True, digits=True
        )

        password = 'qa11111'

        logging.info(f'--- 帳號 {i + 1}/{num_accounts} ---')
        if register_account(user_api, new_account, password):
            successful_registrations += 1

    logging.info('--- 批次註冊完成 ---')
    logging.info(f'成功註冊 {successful_registrations}/{num_accounts} 個帳號。')


# ----------------- Main Execution Block -----------------


def main():
    """
    主函式，用於解析參數並執行腳本。
    """
    parser = argparse.ArgumentParser(description='帳號註冊輔助腳本。')
    parser.add_argument(
        '--env',
        default='qa',
        choices=['dev', 'test', 'pre', 'qa', 'back_qa', 'web_dev'],
        help='API 呼叫的目標環境。',
    )
    parser.add_argument(
        '--num',
        type=int,
        default=1,
        help='要註冊的帳號數量。',
    )
    args = parser.parse_args()

    logging.info(f"在 '{args.env}' 環境上執行腳本。")

    # --- API Client 設定 ---
    try:
        api_config = ReadFileData.read_yaml_data('config', 'config.yml')
        base_url = api_config[args.env]
        user_api = UserAPI(base_url=base_url)
    except KeyError:
        logging.error(f"在 config/config.yml 中找不到環境 '{args.env}'。正在中止。")
        return
    except FileNotFoundError:
        logging.error('找不到 config/config.yml。請確保從專案根目錄執行腳本。正在中止。')
        return
    except Exception as e:
        logging.error(f'設定過程中發生未預期的錯誤: {e}')
        return

    # --- 執行註冊 ---
    generate_and_register_accounts(user_api, args.num)


if __name__ == '__main__':
    main()

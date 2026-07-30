"""產出 Allure 報告所需的中繼資料：環境資訊、歷史紀錄與 executor。

這些都是 session 結束後的檔案操作，與 pytest 的 hook 無關，因此獨立於 conftest。
掛載點是根 conftest 的 `allure_environment_setup` fixture。
"""

import json
import logging
import platform
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def carry_over_history(report_path: Path, result_path: Path) -> int:
    """接續上一份報告的歷史紀錄，並回傳先前最後一次的 build 編號。

    Allure 2 沒有內建的歷史接續機制：`allure generate` 只認 `allure-results/history`，
    而 `--clean-alluredir` 會在 pytest 啟動時清空該目錄。因此複製只能發生在測試跑完
    之後、產報告之前，也就是這裡。少了這一步，Trend 每次都會從零開始而只有一個點。

    編號取自 trend 中最大的 `buildOrder`，而非 trend 的長度。Allure 預設只保留 20 筆
    歷史，用長度會在滿 20 筆後永遠停在同一個編號。最早期的紀錄可能沒有 `buildOrder`
    欄位，一併視為 0。

    Args:
        report_path: 上一份 Allure 報告的目錄。
        result_path: 本次執行的 Allure 結果目錄。

    Returns:
        先前最後一次的 build 編號；沒有可用歷史時回傳 0。
    """
    history_path = report_path / 'history'
    if not history_path.is_dir():
        return 0
    shutil.copytree(history_path, result_path / 'history', dirs_exist_ok=True)
    trend_path = history_path / 'history-trend.json'
    try:
        trend = json.loads(trend_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        logger.warning('讀不到 %s，build 編號改從頭計算', trend_path)
        return 0
    return max((entry.get('buildOrder', 0) for entry in trend), default=0)


def write_executor(source_path: Path, result_path: Path, build_order: int):
    """以專案根目錄的 executor.json 為底，補上 build 編號後寫入 Allure 結果目錄。

    `buildOrder` 是趨勢圖上各 build 的識別碼，沒有它每次執行都會落在同一欄。
    來源檔不會被更動，遞增的編號只存在於本次結果中。

    Args:
        source_path: 專案根目錄的 executor.json。
        result_path: 本次執行的 Allure 結果目錄。
        build_order: 本次執行的 build 編號。
    """
    if not source_path.exists():
        return
    executor = json.loads(source_path.read_text(encoding='utf-8'))
    build_name = executor.get('buildName', 'Local Run')
    executor['buildOrder'] = build_order
    executor['buildName'] = f'{build_name} #{build_order}'
    target_path = result_path / 'executor.json'
    target_path.write_text(json.dumps(executor, ensure_ascii=False, indent=2), encoding='utf-8')


def write_allure_metadata(environment_name: str, urls: str, base_path: Path):
    """寫入 Allure 報告所需的環境資訊、歷史紀錄與 executor 檔案。

    Args:
        environment_name: 當前測試環境的名稱 (例如 'qa', 'dev')。
        urls: 該環境各服務的名稱與位址，以逗號分隔。
        base_path: 專案的根目錄路徑。
    """
    allure_result_path = base_path / 'allure-results'
    allure_result_path.mkdir(parents=True, exist_ok=True)
    environment_path = allure_result_path / 'environment.properties'
    with open(environment_path, 'w') as f:
        f.write(f'os={platform.system()}\n')
        f.write(f'python_version={platform.python_version()}\n')
        f.write(f'environment={environment_name}, {urls}\n')
    build_order = carry_over_history(base_path / 'allure-report', allure_result_path) + 1
    write_executor(base_path / 'executor.json', allure_result_path, build_order)

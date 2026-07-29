import json
import logging
import platform
import shutil
from pathlib import Path

import allure
import pytest

from test_data.common.base import TestCaseData
from utils.config_loader import get_config, set_current_env

# pytest 只改寫測試檔與 conftest 內的斷言。不註冊的話，`case_verify_tool` 裡的
# 比對失敗只會拋出光禿禿的 `AssertionError`，看不到實際值與預期值的差異。
# 必須在該模組被 import 前呼叫，因此放在 conftest 的最上層。
pytest.register_assert_rewrite('utils.case_verify_tool')

logger = logging.getLogger(__name__)


# --- Pytest Hooks ---


def pytest_addoption(parser):
    """為 pytest 新增 `--env` 命令列參數。

    Args:
        parser: pytest 的命令列參數解析器。
    """
    parser.addoption('--env', default='qa', choices=['dev', 'qa'], help='environment parameter')


def pytest_configure(config):
    """在測試開始時，設定要使用的環境名稱

    Args:
        config: pytest 的設定物件。
    """
    env = config.getoption('--env')
    set_current_env(env)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """套用 case 的 Allure 標題與描述，並記錄測項的開始與結束。

    Allure 標籤是**被迫**放在 call 階段：`allure.title` 不是 MarkDecorator，不能像
    其他標籤那樣透過 `create_param_from_case` 掛成 pytest.param 的 mark；而
    `allure.dynamic` 寫在 fixture (setup 階段) 不會有作用，只能用 hookwrapper。
    此寫法對 sync 與 async 測試皆適用。

    日誌是**刻意**放在 call 階段：「開始/結束執行測項」要框住的是測項本身，登入等
    前置條件 (setup 階段) 與密碼還原等清理 (teardown 階段) 都排除在外。改成 autouse
    fixture 會讓它排到最前面，導致前置條件被框進來。

    Args:
        item: 當前執行的測試項目。僅處理參數名為 `case`、型別為 `TestCaseData` 的 parametrize。
    """
    callspec = getattr(item, 'callspec', None)
    case = callspec.params.get('case') if callspec else None
    if isinstance(case, TestCaseData):
        if case.title:
            allure.dynamic.title(case.title)
        if case.description:
            allure.dynamic.description(case.description)

    logger.info('*************** 開始執行測項 ***************')
    yield
    logger.info('*************** 結束執行測項 ***************')


# --- 其他 Hooks ---


def carry_over_history(report_path: Path, result_path: Path) -> int:
    """接續上一份報告的歷史紀錄，並回傳先前已完成的 build 數。

    Allure 2 沒有內建的歷史接續機制：`allure generate` 只認 `allure-results/history`，
    而 `--clean-alluredir` 會在 pytest 啟動時清空該目錄。因此複製只能發生在測試跑完
    之後、產報告之前，也就是這裡。少了這一步，Trend 每次都會從零開始而只有一個點。

    Args:
        report_path: 上一份 Allure 報告的目錄。
        result_path: 本次執行的 Allure 結果目錄。

    Returns:
        先前已完成的 build 數；沒有可用歷史時回傳 0。
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
    return len(trend)


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


@pytest.fixture(scope='session', autouse=True)
def allure_environment_setup(request: pytest.FixtureRequest):
    """在測試 session 結束後，收集報告所需的中繼資料並寫入 Allure 結果目錄。

    位址取自當前環境的設定，而非執行期收集——Allure 的環境區塊描述的是
    「這份報告打的是哪個環境」，屬於整個 launch 不變的資訊。逐次請求打了什麼
    已記錄在各測項的 step 與 log 中。
    """
    yield
    config = get_config()
    urls = dict(config.urls)
    cli_base_url = request.config.getoption('base_url', None)
    if cli_base_url:
        urls['ui'] = cli_base_url
    urls_str = ', '.join(f'{name}={url}' for name, url in sorted(urls.items()))
    base_path = Path(__file__).resolve().parent
    write_allure_metadata(config.env, urls_str, base_path)

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
BASE_PATH = Path(__file__).resolve().parent.parent


class ReadFileData:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def read_yaml_data(directory: str, yaml_file_name: str) -> dict:
        """
        directory: 目標檔案所在資料夾名稱
        yaml_file_name: 目標檔案名稱
        """

        data_file_path = Path('/') / BASE_PATH / directory / yaml_file_name
        logger.info('讀取 %s 文件.....', yaml_file_name)
        with open(data_file_path, encoding='utf-8') as f:
            content = f.read()

        content = os.path.expandvars(content)
        yaml_data = yaml.safe_load(content)

        yaml_data = {key: value for key, value in yaml_data.items() if 'template' not in key}
        logger.info('取得資料 => %s', yaml_data)
        return yaml_data

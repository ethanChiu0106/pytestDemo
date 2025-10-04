"""提供一個用於標準化 API 回應的基礎類別"""
from typing import Union

import humps
import requests
from requests import Response


class ResultBase:
    """標準化 API 回應的基礎類別

    主要功能是將 API 回應 (無論是 `requests.Response` 物件或字典)
    轉換為一個格式統一的字典，並將所有 camelCase 的鍵轉換為 snake_case。
    """

    def __init__(self, response: Union[Response, dict]) -> None:
        """初始化 ResultBase

        Args:
            response: 原始的 API 回應，可以是一個 `requests.Response` 物件，
                      或是一個已解析的字典。
        """
        self.response = response
        self.result = {}

    def get_result(self):
        """處理並回傳標準化後的回應結果

        處理邏輯:
        1. 如果輸入是 `requests.Response` 物件，提取其 `status_code`。
        2. 嘗試將回應的 body 當作 JSON 解析。
        3. 使用 `humps.decamelize` 將所有鍵從駝峰式轉換為蛇式。
        4. 如果 JSON 解析失敗，則直接儲存回應的文字內容。
        5. 如果輸入本身就是字典，直接處理鍵的轉換。

        Returns:
            一個包含標準化結果的字典。
        """
        if isinstance(self.response, requests.models.Response):
            self.result['status_code'] = self.response.status_code
            try:
                self.result.update(humps.decamelize(self.response.json()))
            except ValueError:
                self.result['response_text'] = self.response.text
        else:
            self.result.update(humps.decamelize(self.response))
        return self.result

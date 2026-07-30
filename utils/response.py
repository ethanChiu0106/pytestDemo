"""提供 API 回應的正規化函式"""

from typing import Union

import humps
import requests
from requests import Response


def normalize_response(response: Union[Response, dict]) -> dict:
    """將 API 回應轉為格式統一的字典，並把 camelCase 的鍵轉為 snake_case

    Args:
        response: 原始的 API 回應，可以是 `requests.Response` 物件或已解析的字典。

    Returns:
        標準化後的字典。輸入是 `Response` 時會額外帶入 `status_code`；
        body 不是合法 JSON 時，原始文字放在 `response_text`。
    """
    if not isinstance(response, requests.models.Response):
        return humps.decamelize(response)

    result = {'status_code': response.status_code}
    try:
        result.update(humps.decamelize(response.json()))
    except ValueError:
        result['response_text'] = response.text
    return result

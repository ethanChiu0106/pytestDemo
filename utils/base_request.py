"""提供一個 HTTP 請求的基礎類別"""

import logging
from collections.abc import Mapping
from typing import ClassVar

import allure
import requests

from api.service_names import Service
from utils.response import normalize_response

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = frozenset({'password', 'token', 'authorization', 'cookie'})


def _is_sensitive(key: str) -> bool:
    """判斷欄位名是否屬於敏感欄位

    用子字串比對而非整鍵比對——測試資料的欄位名有 `initial_password`、
    `new_password`、`access_token` 這類變體，整鍵比對會漏掉。
    """
    key = key.lower()
    return any(word in key for word in SENSITIVE_KEYS)


def mask_sensitive(value):
    """遮蔽敏感欄位的值，避免密碼與 token 寫進 log 與 Allure 附件

    比對 `Mapping` 而非 `dict`，因為 requests 的 headers 是 `CaseInsensitiveDict`，
    不是 `dict` 的子類別，只比對 `dict` 會讓 Authorization 整包漏掉。

    Args:
        value: 任意可能含敏感欄位的資料，dict 與 list 會遞迴處理

    Returns:
        同結構的資料，敏感欄位的值換成 '***'
    """
    if isinstance(value, Mapping):
        return {k: '***' if _is_sensitive(k) else mask_sensitive(v) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_sensitive(v) for v in value]
    return value


class BaseRequest:
    """一個 HTTP 請求的基礎類別，封裝了 requests 的常用操作

    子類別必須宣告 `service`，指明自己屬於哪個服務，例如:

        class ItemAPI(BaseRequest):
            service = Service.FRONT
    """

    # 由子類別指定，`ApiClientProvider` 依此決定要使用哪個 base URL
    service: ClassVar[Service]

    def __init__(self, base_url, session=None, default_headers: dict = None):
        """初始化 BaseRequest

        Args:
            base_url: API 的 base URL
            session: 共用的 `requests.Session` 物件。如果未提供，會自動建立一個新的
            default_headers: 此 client 每次請求都會帶上的 headers (例如認證資訊)。
                刻意存放在 client 自身而非 session，避免污染其他共用同一 session 的 client
        """
        self.base_url = base_url
        self.session = session if session else requests.Session()
        self.default_headers = default_headers or {}

    def get(self, path, **kwargs):
        """發送一個 GET 請求

        Args:
            path: API 的路徑
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        return self._send(path, 'GET', **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        """發送一個 POST 請求

        Args:
            path: API 的路徑
            data: 請求的 body 資料，可選
            json: 請求的 body JSON 資料，可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        return self._send(path, 'POST', data, json, **kwargs)

    def put(self, path, data=None, json=None, **kwargs):
        """發送一個 PUT 請求

        Args:
            path: API 的路徑
            data: 請求的 body 資料，可選
            json: 請求的 body JSON 資料，可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        return self._send(path, 'PUT', data, json, **kwargs)

    def delete(self, path, **kwargs):
        """發送一個 DELETE 請求

        Args:
            path: API 的路徑
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        return self._send(path, 'DELETE', **kwargs)

    def _send(self, path: str, method: str, data=None, json: dict = None, **kwargs) -> dict:
        """發送請求、寫入回應日誌並回傳正規化結果 (供四個動詞方法共用)"""
        response = self.request(path, method, data, json, **kwargs)
        self.save_response_log(response)
        return normalize_response(response)

    def request(self, path: str, method: str, data=None, json: dict = None, **kwargs):
        """發送一個 HTTP 請求的核心方法

        headers 的優先序為: 呼叫端傳入的 `headers` > client 的 `default_headers`。
        兩者都只作用於本次請求，不會寫入 `session`，因此不會影響共用同一 session 的其他 client。

        認證資訊請透過 `ApiClientProvider.with_auth()` 建立帶身分的 client 來提供，
        而非在單次呼叫時傳入——身分屬於 client，不屬於單一次請求。

        Allure step 用 context manager 而非裝飾器——裝飾器會把函式引數 (含請求 body
        的密碼) 原文記成 step parameters，報告是公開的，不能讓它進去。

        Args:
            path: API 的路徑
            method: HTTP 請求方法 (例如 'GET', 'POST')
            data: `data` 參數，用於 POST/PUT 等請求，可選
            json: `json` 參數，用於 POST/PUT 等請求，可選
            **kwargs: 其他傳遞給 `requests.request` 的參數 (例如 headers, params)

        Returns:
            一個 `requests.Response` 物件

        Raises:
            requests.RequestException: 當請求失敗時觸發
        """
        with allure.step(f'{method} {path}'):
            try:
                headers = {**self.default_headers, **(kwargs.pop('headers', None) or {})}
                url = self.base_url + path
                self.request_log(url, method, data=data, json=json, **kwargs)
                return self.session.request(method, url, data=data, json=json, headers=headers, **kwargs)
            except requests.RequestException as e:
                logger.error(f'Request failed: {e}')
                raise

    @staticmethod
    def request_log(url: str, method: str, **kwargs):
        """將 HTTP 請求的詳細資訊記錄到日誌中

        Args:
            url: 請求的完整 URL
            method: HTTP 請求方法
            **kwargs: 其他請求參數，如 headers, params, data, json 等
        """
        logger.info('API URL => %s', url)
        logger.info('Method => %s', method)
        for key, value in kwargs.items():
            if value is None:
                continue
            logger.info('Request %s => %s', key, mask_sensitive(value))

    @staticmethod
    def save_response_log(response: requests.Response):
        """將 HTTP 回應的詳細資訊記錄到日誌中

        Args:
            response: 一個 `requests.Response` 物件
        """
        if response is None:
            logger.error('No response received')
            return
        logger.info('Request headers => %s', mask_sensitive(response.request.headers))
        logger.info('Response headers => %s', mask_sensitive(response.headers))
        try:
            response_data = response.json()
            logger.info('Response => %s', mask_sensitive(response_data))
        except ValueError:
            logger.info('Response => %s', response.text)

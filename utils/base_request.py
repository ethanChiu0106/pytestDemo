"""提供一個 HTTP 請求的基礎類別"""

import logging

import allure
import requests

from utils.result_base import ResultBase

logger = logging.getLogger(__name__)


class BaseRequest:
    """一個 HTTP 請求的基礎類別，封裝了 requests 的常用操作"""

    def __init__(self, base_url, session=None):
        """初始化 BaseRequest

        Args:
            base_url: API 的 base URL
            session: 共用的 `requests.Session` 物件。如果未提供，會自動建立一個新的
        """
        self.base_url = base_url
        self.session = session if session else requests.Session()

    def get(self, path, token: str = None, **kwargs):
        """發送一個 GET 請求

        Args:
            path: API 的路徑
            token: 用於此次請求的認證 token, 可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        response = self.request(path, 'GET', token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def post(self, path, data=None, json=None, token: str = None, **kwargs):
        """發送一個 POST 請求

        Args:
            path: API 的路徑
            data: 請求的 body 資料，可選
            json: 請求的 body JSON 資料，可選
            token: 用於此次請求的認證 token, 可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        response = self.request(path, 'POST', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def put(self, path, data=None, json=None, token: str = None, **kwargs):
        """發送一個 PUT 請求

        Args:
            path: API 的路徑
            data: 請求的 body 資料，可選
            json: 請求的 body JSON 資料，可選
            token: 用於此次請求的認證 token, 可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        response = self.request(path, 'PUT', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def delete(self, path, data=None, json=None, token: str = None, **kwargs):
        """發送一個 DELETE 請求

        Args:
            path: API 的路徑
            data: 請求的 body 資料，可選
            json: 請求的 body JSON 資料，可選
            token: 用於此次請求的認證 token, 可選
            **kwargs: 其他傳遞給 `requests.request` 的參數

        Returns:
            一個包含 API 回應結果的 dict
        """
        response = self.request(path, 'DELETE', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    @allure.step('{path}')
    def request(self, path: str, method: str, data=None, json: dict = None, token: str = None, **kwargs):
        """發送一個 HTTP 請求的核心方法

        Args:
            path: API 的路徑
            method: HTTP 請求方法 (例如 'GET', 'POST')
            data: `data` 參數，用於 POST/PUT 等請求，可選
            json: `json` 參數，用於 POST/PUT 等請求，可選
            token: 用於此次請求的認證 token, 可選
            **kwargs: 其他傳遞給 `requests.request` 的參數 (例如 headers, params)

        Returns:
            一個 `requests.Response` 物件

        Raises:
            requests.RequestException: 當請求失敗時觸發
        """
        try:
            if token:
                self.session.headers['Authorization'] = token
            url = self.base_url + path
            self.request_log(url, method, data=data, json=json, **kwargs)
            return self.session.request(method, url, data=data, json=json, **kwargs)
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
            logger.info('Request %s => %s', key, value)

    @staticmethod
    def save_response_log(response: requests.Response):
        """將 HTTP 回應的詳細資訊記錄到日誌中

        Args:
            response: 一個 `requests.Response` 物件
        """
        if response is None:
            logger.error('No response received')
            return
        logger.info('Request headers => %s', response.request.headers)
        logger.info('Response headers => %s', response.headers)
        try:
            response_data = response.json()
            logger.info('Response => %s', response_data)
        except ValueError:
            logger.info('Response => %s', response.text)

import logging

import allure
import requests

from utils.result_base import ResultBase


class BaseRequest:
    def __init__(self, base_url, session=None):
        self.base_url = base_url
        self.session = session if session else requests.Session()

    def get(self, path, token: str = None, **kwargs):
        response = self.request(path, 'GET', token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def post(self, path, data=None, json=None, token: str = None, **kwargs):
        response = self.request(path, 'POST', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def put(self, path, data=None, json=None, token: str = None, **kwargs):
        response = self.request(path, 'PUT', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    def delete(self, path, data=None, json=None, token: str = None, **kwargs):
        response = self.request(path, 'DELETE', data, json, token=token, **kwargs)
        self.save_response_log(response)
        return ResultBase(response).get_result()

    @allure.step('{path}')
    def request(self, path: str, method: str, data=None, json: dict = None, token: str = None, **kwargs):
        """
        發送 HTTP request

        Args:
            path (str): API路徑
            method (str): Request方法
            data (any, optional): Request(POST使用)
            json (dict, optional): Request JSON(POST使用)
            token (str, optional): Authorization token. If provided, it will update the session headers.
            **kwargs: 其他request參數, 如 headers、params、files 等

        Returns:
            requests.Response: HTTP Response
        """
        try:
            if token:
                self.session.headers['Authorization'] = token
            url = self.base_url + path
            self.request_log(url, method, data=data, json=json, **kwargs)
            return self.session.request(method, url, data=data, json=json, **kwargs)
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise

    @staticmethod
    def request_log(url: str, method: str, **kwargs):
        """
        log 寫入request相關資訊

        Args:
        url (str): API URL
        method (str): Request method
        **kwargs: 其他參數，如 headers、params、data、json、files 等
        """
        logging.info('API URL => %s', url)
        logging.info('Method => %s', method)
        for key, value in kwargs.items():
            if value is None:
                continue
            logging.info('Request %s => %s', key, value)

    @staticmethod
    def save_response_log(response):
        if response is None:
            logging.error('No response received')
            return
        logging.info('Request headers => %s', response.request.headers)
        logging.info('Response headers => %s', response.headers)
        try:
            response_data = response.json()
            logging.info('Response => %s', response_data)
        except ValueError:
            logging.info('Response => %s', response.text)

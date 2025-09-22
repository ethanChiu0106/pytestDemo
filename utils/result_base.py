from typing import Union

import humps
import requests
from requests import Response


class ResultBase:
    def __init__(self, response: Union[Response, dict]) -> None:
        self.response = response
        self.result = {}

    def get_result(self):
        if isinstance(self.response, requests.models.Response):
            self.result['status_code'] = self.response.status_code
            try:
                self.result.update(humps.decamelize(self.response.json()))
            except ValueError:
                self.result['response_text'] = self.response.text
        else:
            self.result.update(humps.decamelize(self.response))
        return self.result

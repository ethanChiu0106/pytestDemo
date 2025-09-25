from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from utils.async_base_ws import AsyncBaseWS


class BaseWsApi(ABC):
    def __init__(self, ws_obj: AsyncBaseWS):
        self.ws = ws_obj

    @property
    @abstractmethod
    def op_code(self) -> int:
        """定義這個 API 使用的主要 op_code。"""
        pass

    @property
    @abstractmethod
    def expected_op_code(self) -> int:
        """定義這個 API 預期收到的回應 op_code。"""
        pass

    async def _send_request(self, sub_code: Union[Enum, int], data: dict = None) -> dict:
        """
        通用的請求發送方法。
        可以接收 Enum 成員或整數作為 sub_code。
        """
        sub_code_value = sub_code.value if isinstance(sub_code, Enum) else sub_code

        return await self.ws.send_and_receive(
            op_code=self.op_code, sub_code=sub_code_value, data=data, expected_op_code=self.expected_op_code
        )

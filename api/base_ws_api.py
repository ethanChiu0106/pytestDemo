from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from utils.async_base_ws import AsyncBaseWS


class BaseWsApi(ABC):
    """WebSocket API 的抽象基底類別

    為所有 WebSocket API 提供一個共通的結構和方法，
    強制子類別必須實作 `op_code` 和 `expected_op_code`
    """

    def __init__(self, ws_obj: AsyncBaseWS):
        """初始化 WebSocket API

        Args:
            ws_obj: 一個已連線的 `AsyncBaseWS` 物件，用於收發訊息
        """
        self.ws = ws_obj

    @property
    @abstractmethod
    def op_code(self) -> int:
        """定義此 API 發送訊息時使用的主要操作碼 (op_code)"""
        pass

    @property
    @abstractmethod
    def expected_op_code(self) -> int:
        """定義此 API 回應的預期操作碼 (op_code)"""
        pass

    async def _send_request(self, sub_code: Union[Enum, int], data: dict = None) -> dict:
        """發送一個 WebSocket 請求並等待回應。

        會自動處理 `sub_code` 的轉換 (Enum 或 int), 並呼叫底層的 `ws.send_and_receive`

        Args:
            sub_code: 次操作碼，可以是 Enum 或 int。
            data: 要發送的請求資料，可選

        Returns:
            一個包含 API 回應結果的字典
        """
        sub_code_value = sub_code.value if isinstance(sub_code, Enum) else sub_code

        return await self.ws.send_and_receive(
            op_code=self.op_code, sub_code=sub_code_value, data=data, expected_op_code=self.expected_op_code
        )

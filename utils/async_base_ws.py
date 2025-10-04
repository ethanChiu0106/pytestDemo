import asyncio
import gzip
import logging

import allure
import msgpack
import websockets

from api.ws_constants import OpCode
from utils.result_base import ResultBase

logger = logging.getLogger(__name__)


class AsyncBaseWS:
    """一個非同步 WebSocket 客戶端，負責處理連線、訊息收發與心跳"""

    def __init__(self, ws_url: str, receive_init_msgs: bool = True) -> None:
        """初始化 WebSocket 客戶端

        Args:
            ws_url: 要連接的 WebSocket 伺服器 URL
            receive_init_msgs: 是否在連線後等待接收初始訊息 (例如 player_init_info)
        """
        self.ws_url = ws_url
        self.receive_init_msgs = receive_init_msgs
        self._websocket: websockets.WebSocketClientProtocol | None = None
        self.polling_task: asyncio.Task | None = None
        self.listener_task: asyncio.Task | None = None
        self.message_queue = asyncio.Queue()
        self.unsolicited_messages = asyncio.Queue()
        self.player_init_info = None

    async def connect(self):
        """建立 WebSocket 連線，並啟動背景監聽和心跳任務"""
        self._websocket = await websockets.connect(self.ws_url)

        # 啟動背景任務來持續監聽所有傳入的訊息
        self.listener_task = asyncio.create_task(self.listen_for_messages())

        # 根據旗標，決定是否接收連線後的初始訊息
        if self.receive_init_msgs:
            message = await self.receive_msg()
            if message and 'data' in message:
                self.player_init_info = message['data']
            else:
                logger.error(f'接收到的初始訊息格式不正確或為空: {message}')

        # 啟動定期發送 Ping 的心跳任務
        self.polling_task = asyncio.create_task(self.polling_ping())

    async def listen_for_messages(self):
        """持續監聽來自 WebSocket 的所有訊息

        此方法作為一個背景任務執行
        - Pong 訊息會被直接記錄
        - 其他所有訊息會被解包後放入 `message_queue` 等待處理
        """
        try:
            while True:
                response = await self._websocket.recv()
                data = self.unpack_msg(response)

                if data.get('op_code') == OpCode.S2CPong.value:
                    logger.debug(f'Received pong: {data}')
                else:
                    await self.message_queue.put(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info('監聽任務停止：連線已關閉')
        except asyncio.CancelledError:
            logger.info('監聽任務已被取消')
        except Exception as e:
            logger.error(f'監聽任務發生錯誤: {e}', exc_info=True)

    @staticmethod
    def _pack_msg(data: dict) -> bytes:
        """將字典打包成 WebSocket 傳輸用的二進位格式

        Args:
            data: 準備發送的訊息 dict

        Returns:
            經過 msgpack 打包和 gzip 壓縮 (如果需要) 的位元組
        """
        if 'data' in data and data['data'] is not None:
            data['data'] = msgpack.packb(data['data'])
        msg_pack = msgpack.packb(data)
        if len(msg_pack) >= 250:
            msg_pack = b'\x01' + gzip.compress(msg_pack)
        else:
            msg_pack = b'\x00' + msg_pack
        return msg_pack

    async def send_msg(self, data_dict: dict):
        """打包並發送一則訊息到 WebSocket 伺服器

        Args:
            data_dict: 要發送的訊息內容
        """
        c2s_data = {k: v for k, v in data_dict.items() if v is not None}
        log_level = logging.DEBUG if c2s_data.get('op_code') == OpCode.C2SPing.value else logging.INFO
        logger.log(log_level, 'Send => %s', c2s_data)
        content = self._pack_msg(c2s_data)

        logger.debug('msgpack data => %s', content)
        if self._websocket:
            try:
                await self._websocket.send(content)
            except websockets.exceptions.ConnectionClosed:
                logger.warning('WebSocket 連線已關閉，無法發送訊息')
        else:
            logger.warning('WebSocket 尚未連線，無法發送訊息')

    async def send_and_receive(
        self,
        op_code: int,
        expected_op_code: int,
        sub_code: int = None,
        data: dict = None,
        timeout: int = 5,
    ) -> dict:
        """發送一則訊息，並等待符合預期的回應

        Args:
            op_code: 要發送訊息的主要操作碼
            expected_op_code: 預期回應訊息的主要操作碼
            sub_code: 要發送訊息的子操作碼，可選
            data: 要發送的業務資料，可選
            timeout: 等待回應的秒數，預設為 5 秒

        Returns:
            包含 API 回應結果的 dict, 若超時則回傳錯誤訊息 dict
        """
        if not self._websocket:
            logger.error('WebSocket 尚未連線')
            return {'status_code': 500, 'message': 'WebSocket not connected'}

        dict_data = {
            'op_code': op_code,
            'sub_code': sub_code,
            'data': data,
        }
        await self.send_msg(dict_data)

        try:
            async with asyncio.timeout(timeout):
                while True:
                    response_data = await self.message_queue.get()
                    if response_data.get('op_code') == expected_op_code:
                        logger.info('Receive (Expected) => %s', response_data)
                        result = ResultBase(response_data).get_result()
                        return result
                    else:
                        print(f'Received (Unexpected) => {response_data}')
                        logger.warning('等待 op_code %s 時收到非預期訊息: %s', expected_op_code, response_data)
                        await self.unsolicited_messages.put(response_data)

        except TimeoutError:
            logger.error('超時：在 %s 秒內未收到期望的 op_code %s', timeout, expected_op_code)
            return {'status_code': 408, 'message': f'Timeout waiting for op_code {expected_op_code}'}

    async def receive_msg(self) -> dict:
        """從訊息佇列中獲取下一則訊息

        此方法不進行 op_code 過濾，直接回傳佇列中的下一則訊息

        Returns:
            一個包含 API 回應結果的 dict
        """
        if self._websocket:
            data = await self.message_queue.get()
            logger.info('Receive => %s', data)
            result = ResultBase(data).get_result()
            return result
        else:
            logger.error('WebSocket 尚未連線或已關閉，無法接收訊息')
            return {'status_code': 500, 'message': 'WebSocket not connected'}

    @staticmethod
    def unpack_msg(msgpack_data: bytes) -> dict:
        """解包從伺服器收到的二進位訊息

        此方法會自動處理 gzip 解壓縮

        Args:
            msgpack_data: 從 WebSocket 收到的原始位元組

        Returns:
            解包和解壓後的 dict
        """
        if msgpack_data.startswith(b'\x01'):
            msgpack_data = gzip.decompress(msgpack_data[1:])
        else:
            msgpack_data = msgpack_data[1:]

        msg = msgpack.unpackb(msgpack_data)

        if 'data' in msg and isinstance(msg['data'], bytes):
            raw_data = msgpack.unpackb(msg['data'])
            msg['data'] = raw_data
        return msg

    async def polling_ping(self):
        """作為背景任務，定期發送 Ping 訊息以保持連線活躍"""
        dict_data = {'op_code': OpCode.C2SPing.value}
        try:
            while True:
                print('Sending ping...')
                await self.send_msg(dict_data)
                await asyncio.sleep(7)
        except asyncio.CancelledError:
            logger.info('心跳任務已被取消')
        except websockets.exceptions.ConnectionClosed:
            logger.info('心跳任務停止：連線已關閉')
        except Exception as e:
            logger.error(f'心跳任務發生錯誤: {e}', exc_info=True)

    async def stop_listener(self):
        """安全地停止背景的訊息監聽任務"""
        if self.listener_task and not self.listener_task.done():
            logger.info('正在取消監聽任務...')
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                logger.info('監聽任務已成功取消')
        else:
            logger.info('監聽任務未在執行或已完成')

    async def stop_polling(self):
        """安全地停止背景的心跳任務"""
        if self.polling_task and not self.polling_task.done():
            logger.info('正在取消心跳任務...')
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                logger.info('心跳任務已成功取消')
        else:
            logger.info('心跳任務未在執行或已完成')

    @allure.step('關閉 WebSocket 連線')
    async def close_connect(self):
        """依序停止所有背景任務，並關閉 WebSocket 連線"""
        await self.stop_polling()
        await self.stop_listener()
        if self._websocket:
            await self._websocket.close()
            logger.info('WebSocket 連線已關閉')
        else:
            logger.info('WebSocket 已關閉或不存在')

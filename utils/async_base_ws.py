import asyncio
import gzip
import logging

import allure
import msgpack
import websockets

from api.ping import Ping
from utils.result_base import ResultBase

logger = logging.getLogger(__name__)


class AsyncBaseWS:
    """
    一個非同步 WebSocket 客戶端的基礎類別，用於處理連線、訊息收發和背景任務。
    它使用 asyncio 來管理並行的網路操作，並透過佇列來解耦訊息的接收與處理。
    """

    def __init__(self, ws_url: str, receive_init_msgs: bool = True) -> None:
        """
        初始化 WebSocket 客戶端。

        :param ws_url: 要連接的 WebSocket 伺服器 URL。
        :param receive_init_msgs: 是否在連線後等待接收初始訊息 (player_init_info)。
        """
        self.init_notice = None  # 儲存初始通知訊息
        self.ws_url = ws_url  # WebSocket 伺服器 URL
        self.receive_init_msgs = receive_init_msgs  # 控制是否接收初始訊息的旗標
        self._websocket: websockets.WebSocketClientProtocol | None = None  # WebSocket 連線物件
        self.polling_task: asyncio.Task | None = None  # 背景心跳任務
        self.listener_task: asyncio.Task | None = None  # 背景訊息監聽任務
        self.message_queue = asyncio.Queue()  # 用於存放已接收訊息的主佇列
        self.unsolicited_messages = asyncio.Queue()  # 用於存放非預期(或伺服器主動推送)的訊息
        self.player_init_info = None  # 儲存玩家的初始資訊

    async def connect(self):
        """
        建立與 WebSocket 伺服器的連線，並啟動背景監聽和心跳任務。
        這個方法會依序執行以下操作：
        1. 建立 WebSocket 連線。
        2. 啟動一個背景任務 (`listener_task`) 來持續監聽所有傳入的訊息。
        3. 從訊息佇列中接收預期的初始訊息。
        4. 啟動另一個背景任務 (`polling_task`) 來定期發送心跳 Ping。
        """
        # 建立 WebSocket 連線
        self._websocket = await websockets.connect(self.ws_url)

        # 優先啟動監聽任務，確保不會錯過任何伺服器訊息
        self.listener_task = asyncio.create_task(self.listen_for_messages())

        # 根據初始化旗標，決定如何處理連線後的初始訊息
        if self.receive_init_msgs:
            # Game WS: 等待 player_init_info
            self.player_init_info = await self.receive_msg()

        # 啟動定期發送 Ping 的心跳任務
        self.polling_task = asyncio.create_task(self.polling_ping())

    async def listen_for_messages(self):
        """
        作為一個背景任務，持續監聽來自 WebSocket 的所有訊息。
        - Pong 訊息 (op_code 2) 會被直接記錄。
        - 其他訊息會被解包後放入 `message_queue`。
        """
        try:
            # 當連線存在且未關閉時，無限循環地接收訊息
            while self._websocket and not self._websocket.closed:
                response = await self._websocket.recv()  # 非同步等待接收訊息
                data = self.unpack_msg(response)

                # 如果是 Pong 回應，直接印出和記錄，不放入佇列
                if data.get('op_code') == 2:
                    logger.info(f'Received pong: {data}')
                else:
                    # 其他所有訊息都放入主佇列
                    await self.message_queue.put(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info('監聽任務停止：連線已關閉。')
        except asyncio.CancelledError:
            logger.info('監聽任務已被取消。')
        except Exception as e:
            logger.error(f'監聽任務發生錯誤: {e}', exc_info=True)

    async def send_msg(self, content: bytes):
        """
        發送一則訊息到 WebSocket 伺服器。

        :param content: 要發送的訊息內容 (bytes)。
        """
        logger.debug('msgpack data => %s', content)
        if self._websocket and not self._websocket.closed:
            await self._websocket.send(content)
        else:
            logger.warning('WebSocket 尚未連線或已關閉，無法發送訊息。')

    async def send_and_receive(self, msg_content: bytes, expected_op_code: int, timeout: int = 5) -> dict:
        """
        發送一則訊息，並在指定的超時時間內，等待並篩選特定 op_code 的回應。

        :param msg_content: 要發送的請求訊息內容。
        :param expected_op_code: 期望收到的回應訊息中的 op_code。
        :param timeout: 等待回應的超時時間（秒）。
        :return: 收到的符合條件的回應訊息，或在超時/錯誤時返回錯誤訊息。
        """
        logger.debug('msgpack data => %s', msg_content)
        if not (self._websocket and not self._websocket.closed):
            logger.error('WebSocket 尚未連線或已關閉。')
            return {'status_code': 500, 'message': 'WebSocket not connected'}

        await self._websocket.send(msg_content)

        try:
            # 使用 asyncio.timeout 來實現超時控制
            async with asyncio.timeout(timeout):
                while True:
                    # 從主佇列中獲取由 listener 放入的訊息
                    data = await self.message_queue.get()
                    # 檢查 op_code 是否是我們期望的
                    if data.get('op_code') == expected_op_code:
                        logger.info('Receive (Expected) => %s', data)
                        result = ResultBase(data).get_result()
                        return result
                    else:
                        # 如果不是期望的訊息，則視為非預期訊息
                        print(f'Received (Unexpected) => {data}')
                        logger.warning('等待 op_code %s 時收到非預期訊息: %s', expected_op_code, data)
                        # 將它存入另一個佇列，以備後續處理或檢查
                        await self.unsolicited_messages.put(data)

        except TimeoutError:
            logger.error('超時：在 %s 秒內未收到期望的 op_code %s。', timeout, expected_op_code)
            return {'status_code': 408, 'message': f'Timeout waiting for op_code {expected_op_code}'}

    async def receive_msg(self) -> dict:
        """
        從訊息佇列中獲取並返回下一則訊息，不進行 op_code 過濾。
        主要用於接收順序固定或伺服器主動推送的訊息。

        :return: 佇列中的下一則訊息。
        """
        if self._websocket and not self._websocket.closed:
            # 直接從佇列中取出訊息
            data = await self.message_queue.get()
            logger.info('Receive => %s', data)
            result = ResultBase(data).get_result()
            return result
        else:
            logger.error('WebSocket 尚未連線或已關閉，無法接收訊息。')
            return {'status_code': 500, 'message': 'WebSocket not connected'}

    async def wait_for_message(self, expected_op_code: int, timeout: int = 5) -> dict:
        """
        在指定的超時時間內，等待並篩選特定 op_code 的訊息，但不發送任何請求。
        主要用於處理伺服器在連線後主動推送的確認訊息。

        :param expected_op_code: 期望收到的回應訊息中的 op_code。
        :param timeout: 等待回應的超時時間（秒）。
        :return: 收到的符合條件的回應訊息，或在超時/錯誤時返回錯誤訊息。
        """
        if not (self._websocket and not self._websocket.closed):
            logger.error('WebSocket 尚未連線或已關閉。')
            return {'status_code': 500, 'message': 'WebSocket not connected'}

        try:
            # 使用 asyncio.timeout 來實現超時控制
            async with asyncio.timeout(timeout):
                while True:
                    # 從主佇列中獲取由 listener 放入的訊息
                    data = await self.message_queue.get()

                    # 檢查 op_code 是否是我們期望的
                    if data.get('op_code') == expected_op_code:
                        logger.info('Receive (Expected) => %s', data)
                        result = ResultBase(data).get_result()
                        return result
                    else:
                        # 如果不是期望的訊息，則視為非預期訊息
                        logger.warning('等待 op_code %s 時收到非預期訊息: %s', expected_op_code, data)
                        # 將它存入另一個佇列，以備後續處理或檢查
                        await self.unsolicited_messages.put(data)

        except TimeoutError:
            logger.error('超時：在 %s 秒內未收到期望的 op_code %s。', timeout, expected_op_code)
            return {'status_code': 408, 'message': f'Timeout waiting for op_code {expected_op_code}'}

    @staticmethod
    def unpack_msg(msgpack_data: bytes) -> dict:
        """
        解包從伺服器收到的二進位訊息。
        處理兩種情況：
        1. 訊息以 `0x01` 開頭，表示後續內容經過 gzip 壓縮。
        2. 訊息沒有 `0x01` 開頭，直接是 msgpack 內容。
        若有 'data' 欄位，則會再解包該內容。

        :param msgpack_data: 從 WebSocket 收到的原始位元組。
        :return: 解包和解壓後的 Python 字典。
        """
        # 檢查第一個位元組是否為 gzip 壓縮標誌
        if msgpack_data.startswith(b'\x01'):
            # 如果是，則跳過標誌位並解壓縮
            msgpack_data = gzip.decompress(msgpack_data[1:])
        else:
            # 如果不是，僅跳過標誌位
            msgpack_data = msgpack_data[1:]

        # 使用 msgpack 解包第一層
        msg = msgpack.unpackb(msgpack_data)

        # 檢查 'data' 欄位是否存在且其值仍為位元組，如果是，則進行第二層解包
        if 'data' in msg and isinstance(msg['data'], bytes):
            raw_data = msgpack.unpackb(msg['data'])
            msg['data'] = raw_data
        return msg

    async def polling_ping(self):
        """
        心跳機制
        作為一個背景任務，定期（每7秒）向伺服器發送 Ping 訊息以保持連線活躍。
        """
        data = Ping().c2s_data()  # 準備 Ping 訊息
        try:
            while True:
                print('Sending ping...')
                await self.send_msg(data)
                await asyncio.sleep(7)  # 非同步等待7秒
        except asyncio.CancelledError:
            logger.info('心跳任務已被取消。')
        except websockets.exceptions.ConnectionClosed:
            logger.info('心跳任務停止：連線已關閉。')
        except Exception as e:
            logger.error(f'心跳任務發生錯誤: {e}', exc_info=True)

    async def stop_listener(self):
        """
        停止背景的訊息監聽任務。
        """
        if self.listener_task and not self.listener_task.done():
            logger.info('正在取消監聽任務...')
            self.listener_task.cancel()  # 發出取消請求
            try:
                await self.listener_task  # 等待任務確實完成取消(若成功取消會引發CancelledError)
            except asyncio.CancelledError:
                logger.info('監聽任務已成功取消。')
        else:
            logger.info('監聽任務未在執行或已完成。')

    async def stop_polling(self):
        """
        停止背景的心跳任務。
        """
        if self.polling_task and not self.polling_task.done():
            logger.info('正在取消心跳任務...')
            self.polling_task.cancel()  # 發出取消請求
            try:
                await self.polling_task  # 等待任務確實完成取消
            except asyncio.CancelledError:
                logger.info('心跳任務已成功取消。')
        else:
            logger.info('心跳任務未在執行或已完成。')

    @allure.step('關閉 WebSocket 連線')
    async def close_connect(self):
        """
        關閉 WebSocket 連線。
        會依序停止心跳任務、監聽任務，最後才關閉底層的 WebSocket 連線。
        """
        await self.stop_polling()
        await self.stop_listener()
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
            logger.info('WebSocket 連線已關閉。')
        else:
            logger.info('WebSocket 已關閉或不存在。')

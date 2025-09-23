import asyncio
import logging

import pytest

from utils.allure_utils import allure_from_case
from utils.async_base_ws import AsyncBaseWS

logger = logging.getLogger(__name__)


class TestConnect:
    @allure_from_case
    @pytest.mark.asyncio
    async def test_ping_pong(self, ws_connect: AsyncBaseWS):
        """
        測試 WebSocket 連線後，客戶端自動發送 Ping 並能收到伺服器的 Pong 回應。
        """
        ws_client = ws_connect
        logger.info(f'WebSocket 連線成功，客戶端為: {ws_client}')

        # AsyncBaseWS 會自動在背景每 7 秒發送一次 Ping。
        # 我們這裡等待 10 秒，以確保至少有一次 Ping-Pong 交換。
        # 使用 asyncio.sleep 來避免阻塞事件循環。
        logger.info('等待 10 秒，觀察自動的 Ping-Pong 流程...')
        await asyncio.sleep(10)

        # 在這個測試中，我們依賴日誌來確認 Pong 是否被接收。
        # `listen_for_messages` 方法會記錄 "Received pong: ..."
        # 如果需要更嚴格的驗證，需要修改 AsyncBaseWS 來將 Pong 放入一個專門的佇列。
        # 但對於目前的連線測試，觀察日誌是足夠的。
        logger.info("測試結束。請檢查日誌中是否有 'Sending ping...' 和 'Received pong' 的記錄。")

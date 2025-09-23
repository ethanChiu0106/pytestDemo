import gzip
import logging

import msgpack

logger = logging.getLogger(__name__)


class Common:
    def __init__(self) -> None:
        self.op_code = None

    @staticmethod
    def __pack_msg(data: dict) -> bytes:
        if 'data' in data:
            data['data'] = msgpack.packb(data['data'])
        msg_pack = msgpack.packb(data)
        if len(msg_pack) >= 250:
            msg_pack = b'\x01' + gzip.compress(msg_pack)
        else:
            msg_pack = b'\x00' + msg_pack
        return msg_pack

    def c2s_data(self, sub_code=None, **kwargs) -> bytes:
        dict_data = {
            'op_code': self.op_code,
            'sub_code': sub_code,
            'data': kwargs.get('data'),
            'memo': kwargs.get('memo'),
        }

        c2s_data = {k: v for k, v in dict_data.items() if v is not None}
        log_level = logging.DEBUG if c2s_data['op_code'] == 1 else logging.INFO
        logger.log(log_level, 'Send => %s', c2s_data)
        return self.__pack_msg(c2s_data)

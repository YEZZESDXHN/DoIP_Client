import abc
from enum import Enum
from typing import Dict, Type, Optional, Union

import crcmod.predefined  # 使用 crcmod 库


class ChecksumType(str, Enum):
    # 使用 str, Enum 混合通常对 Pydantic 更友好，序列化直接出字符串
    crc32 = 'crc32'
    md5 = 'md5'
    sha256 = 'sha256'


# 定义一个抽象基类 (Interface)，规范所有算法必须长什么样
class ChecksumStrategy(abc.ABC):
    @abc.abstractmethod
    def calculate(self, data: bytes) -> bytes:
        """输入字节数据，返回校验和字符串 (通常是 Hex)"""
        pass


# 实现 CRC32 策略 (使用 crcmod)
class CRC32Strategy(ChecksumStrategy):
    def __init__(self):
        # 初始化 crc-32 算法，使用 crcmod 的预定义配置
        self._crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')

    def calculate(self, data: bytes) -> bytes:
        # crcmod 返回的是 int，我们需要转成 hex 字符串
        checksum_int = self._crc_func(data)
        try:
            return checksum_int.to_bytes(length=4, byteorder='big', signed=False)
        except Exception as e:
            raise e


ALGORITHM_REGISTRY: Dict[ChecksumType, Type[ChecksumStrategy]] = {
    ChecksumType.crc32: CRC32Strategy,
}
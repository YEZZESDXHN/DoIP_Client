from time import sleep
from types import SimpleNamespace
from typing import Optional

from PySide6.QtCore import QObject, Signal
from udsoncan import Response

# from typing import TYPE_CHECKING
import utils
from FirmwareFileParser import FirmwareFileParser
from UDSClient import QUDSClient


# if TYPE_CHECKING:
#     from UDSClient import QUDSClient


class ScriptAPI:
    def __init__(self, uds_client: QUDSClient, write_signal: Signal(str), script_name):
        self._uds_client: QUDSClient = uds_client
        self._utils = SimpleNamespace()
        self._utils.hex_str_to_bytes = utils.hex_str_to_bytes
        self.write_signal: Signal(str) = write_signal
        self.script_name = script_name
        self.firmware_file_parser = FirmwareFileParser()
        self.version = "1.0.0"

    def uds_send_and_wait_response(self, payload: bytes) -> Optional[Response]:
        # 执行核心请求
        response = self._uds_client._execute_uds_request(payload, log_prefix="api:")

        # 扩展功能：在此处添加报告打印逻辑
        # if response:
        #     self._generate_api_report(response)

        return response

    @property
    def uds_security_key(self) -> bytes:
        return self._uds_client.security_key

    @property
    def uds_security_seed(self) -> bytes:
        return self._uds_client.security_seed

    def hex_str_to_bytes(self, hex_str: str) -> bytes:
        return self._utils.hex_str_to_bytes(hex_str)

    @staticmethod
    def sleep(secs: float) -> None:
        sleep(secs)

    def write(self, text: str):
        self.write_signal.emit(self.script_name, text)



from datetime import datetime
from time import sleep
from types import SimpleNamespace
from typing import Optional, List, Union
import html

from PySide6.QtCore import Signal
# from typing import TYPE_CHECKING

from udsoncan import Response

from app import utils
from app.core.FirmwareFileParser import FirmwareFileParser
from app.core.uds_client import QUDSClient




# if TYPE_CHECKING:
#     from UDSClient import QUDSClient


class ScriptAPI:
    def __init__(self, uds_client: QUDSClient, write_signal: Signal(str), script_name=''):
        self._uds_client: QUDSClient = uds_client
        self._utils = SimpleNamespace()
        self._utils.hex_str_to_bytes = utils.hex_str_to_bytes
        self.write_signal: Signal(str) = write_signal
        self.script_name = script_name
        self.firmware_file_parser = FirmwareFileParser()
        self.version = "1.0.0"

        self.report_steps = []
        self._is_success = True

    def _reset_report_state(self):
        """重置 API 状态，供 Runner/Plugin 调用"""
        self.report_steps.clear()
        self._is_success = True

    def _add_step_record(self, step_type: str, title: str, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None, result=""):
        """内部方法：记录步骤"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.report_steps.append({
            "timestamp": timestamp,
            "type": step_type,
            "title": title,
            "data": data,
            "result": result
        })

    def test_step(self, title: str, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        self._add_step_record("Step", title, data, "")

    def test_step_pass(self, title, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        self._add_step_record("Check", title, data, "Pass")

    def test_step_fail(self, title, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        self._add_step_record("Check", title, data, "Fail")
        self._is_success = False

    def uds_send_and_wait_response(self, payload: bytes) -> Optional[Response]:
        # 执行核心请求
        response = self._uds_client._execute_uds_request(payload, log_prefix="api:")

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



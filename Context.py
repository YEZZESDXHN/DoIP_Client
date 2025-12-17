from types import SimpleNamespace
# from typing import TYPE_CHECKING
import utils
# if TYPE_CHECKING:
#     from UDSClient import QUDSClient


class RuntimeContext:
    def __init__(self, uds_client):
        self.uds_client = uds_client
        self.utils = SimpleNamespace()
        self.utils.hex_str_to_bytes = utils.hex_str_to_bytes
        self.version = "1.0.0"

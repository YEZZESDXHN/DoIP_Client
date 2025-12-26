from PySide6.QtCore import Signal, QObject

from UDSClient import QUDSClient
from UI.FlashConfigPanel import FlashConfig


class QFlashExecutor(QObject):
    write_signal = Signal(str, str)

    def __init__(self, uds_client: QUDSClient, flash_config: FlashConfig, flash_file_paths: dict):
        super().__init__()
        self.uds_client = uds_client

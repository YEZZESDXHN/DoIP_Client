from PySide6.QtCore import Signal, QObject

from FirmwareFileParser import FirmwareFileParser
from UDSClient import QUDSClient
from UI.FlashConfigPanel import FlashConfig
from global_variables import gFlashVars


class QFlashExecutor(QObject):
    write_signal = Signal(str, str)

    def __init__(self, uds_client: QUDSClient, flash_config: FlashConfig, flash_file_paths: dict):
        super().__init__()
        self.uds_client = uds_client
        self.flash_config = flash_config
        self.flash_file_paths = flash_file_paths
        self.flash_file_parsers: dict[str: FirmwareFileParser] = {}
        self.flash_vars = gFlashVars

    def start_flash(self):
        self.flash_file_parsers.clear()
        for file in self.flash_config.files:
            self.flash_file_parsers[file.name] = FirmwareFileParser()
            self.flash_file_parsers[file.name].load(self.flash_file_paths[file.name])

    def stop_flash(self):
        print(self.flash_vars)



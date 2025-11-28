import ipaddress
import logging

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from DoIPConfigUI import Ui_Dialog
from utils import hex_str_to_int

logger = logging.getLogger("UDSOnIPClient")


class DoIPConfigPanel(QDialog, Ui_Dialog):
    """
    配置面板类，继承自 QDialog (窗口行为) 和 Ui_Dialog (界面布局)
    """

    config_signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.send_config_signal)

    @Slot()
    def send_config_signal(self):
        try:
            if self.lineEdit_TesterLogicalAddress.text():
                tester_logical_address = hex_str_to_int(self.lineEdit_TesterLogicalAddress.text())
            else:
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    'tester logical address 输入为空',  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error('tester logical address 输入为空')
                return
        except Exception as e:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                str(e),  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.exception(e)
            return

        try:
            if self.lineEdit_TesterLogicalAddress.text():
                DUT_logical_address = hex_str_to_int(self.lineEdit_DUTLogicalAddress.text())
            else:
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    'DUT logical address 输入为空',  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error('DUT logical address 输入为空')
                return
        except Exception as e:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                str(e),  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.exception(e)
            return

        if self.lineEdit_DUT_IP.text():
            DUT_ip_raw_str = self.lineEdit_DUT_IP.text()
            ip_object = ipaddress.ip_address(DUT_ip_raw_str)
            if ip_object.version == 4:
                DUT_ipv4_address = DUT_ip_raw_str
            else:
                error_message = f'DUT IPv4输入错误:{DUT_ip_raw_str}'
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    error_message,  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error(error_message)
                return
        else:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                'DUT IP 输入为空',  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.error('DUT IP 输入为空')
            return
        config = {'tester_logical_address': tester_logical_address,
                  'DUT_logical_address': DUT_logical_address,
                  'DUT_ipv4_address': DUT_ipv4_address}
        self.config_signal.emit(config)
        self.accept()

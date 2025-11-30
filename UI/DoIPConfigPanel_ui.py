import ipaddress
import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from UI.DoIPConfigUI import Ui_DoIPConfig
from utils import hex_str_to_int


logger = logging.getLogger("UiCustom")

# -------------------------- 配置面板类 --------------------------
class DoIPConfigPanel(QDialog, Ui_DoIPConfig):
    """
    配置面板类，继承自 QDialog (窗口行为) 和 Ui_Dialog (界面布局)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.config = {}
        self.buttonBox.accepted.connect(self._on_accept)

    @Slot()
    def _on_accept(self):
        """校验输入（捕获异常）"""
        tester_logical_address = self.lineEdit_TesterLogicalAddress.text()
        DUT_logical_address = self.lineEdit_DUTLogicalAddress.text()
        DUT_ipv4_address = self.lineEdit_DUT_IP.text()

        if not tester_logical_address:
            QMessageBox.warning(self, "输入错误", "Tester逻辑地址不能为空！")
            self.lineEdit_TesterLogicalAddress.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = tester_logical_address.strip()
            try:
                self.config['tester_logical_address'] = hex_str_to_int(text)
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "Tester逻辑地址输入错误",
                    f"数据格式非法！\n错误原因：{str(e)}\n请输入合法的十六进制字符串（如1A3F、FF00）。"
                )
                self.lineEdit_TesterLogicalAddress.setFocus()  # 聚焦到输入框重新输入
                return

        if not DUT_logical_address:
            QMessageBox.warning(self, "输入错误", "DUT逻辑地址不能为空！")
            self.lineEdit_DUTLogicalAddress.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = DUT_logical_address.strip()
            try:
                self.config['DUT_logical_address'] = hex_str_to_int(text)
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "DUT逻辑地址输入错误",
                    f"数据格式非法！\n错误原因：{str(e)}\n请输入合法的十六进制字符串（如1A3F、FF00）。"
                )
                self.lineEdit_DUTLogicalAddress.setFocus()  # 聚焦到输入框重新输入
                return

        if not DUT_ipv4_address:
            QMessageBox.warning(self, "输入错误", "DUT IP地址不能为空！")
            self.lineEdit_DUT_IP.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = DUT_ipv4_address.strip()
            try:
                ip_obj = ipaddress.ip_address(text)
                if ip_obj.version != 4:
                    QMessageBox.critical(
                        self,
                        "DUT IP地址输入错误",
                        f"数据格式非法！\n仅支持IPv4地址，当前输入为IPv{ip_obj.version}：{text}"
                    )
                self.config['DUT_ipv4_address'] = text
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "DUT IP地址输入错误",
                    f"仅支持IPv4地址"
                )
                self.lineEdit_DUT_IP.setFocus()  # 聚焦到输入框重新输入
                return

            # 校验通过，关闭对话框
            self.accept()
import ipaddress
import logging
from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from UI.DoIPConfigUI import Ui_DoIPConfig
from user_data import DoIPConfig
from utils import hex_str_to_int


logger = logging.getLogger("UiCustom")

# -------------------------- 配置面板类 --------------------------
class DoIPConfigPanel(QDialog, Ui_DoIPConfig):
    """
    配置面板类，继承自 QDialog (窗口行为) 和 Ui_Dialog (界面布局)
    """

    def __init__(self, parent=None, is_create_new_config: bool = False, configs_name: list[str] = []):
        super().__init__(parent)
        self.setupUi(self)
        self.config: Optional[DoIPConfig] = DoIPConfig(
            config_name='DoIP_config_panel_default',
            tester_logical_address=0x7e2,
            dut_logical_address=0x773,
            dut_ipv4_address='172.16.104.70'
        )
        self.configs_name = configs_name
        self.is_create_new_config = is_create_new_config
        self.is_delete_config = False
        self.buttonBox.accepted.connect(self._on_accept)
        self.pushButton_delete.clicked.connect(self._on_delete_config)
        # self.setWindowIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton))

        if not self.is_create_new_config:
            self.lineEdit_ConfigName.setDisabled(True)
            self.label_ConfigName.setDisabled(True)
        else:
            self.pushButton_delete.setVisible(False)

    def _on_delete_config(self):
        self.is_delete_config = True
        self._on_accept()

    @Slot()
    def _on_accept(self):
        """校验输入（捕获异常）"""
        config_name = self.lineEdit_ConfigName.text()
        tester_logical_address = self.lineEdit_TesterLogicalAddress.text()
        DUT_logical_address = self.lineEdit_DUTLogicalAddress.text()
        DUT_ipv4_address = self.lineEdit_DUT_IP.text()

        if self.is_delete_config:
            reply = QMessageBox.warning(
                self,
                "删除配置",
                f"确认删除配置{self.config.config_name}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # 设置要显示的按钮
                QMessageBox.StandardButton.No  # 设置默认焦点按钮 (推荐 No，防止误删)
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config = None
                self.accept()
                return
            else:
                return

        if not config_name:
            QMessageBox.warning(self, "输入错误", "配置名称不能为空！")
            self.lineEdit_ConfigName.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            if self.is_create_new_config:
                if config_name in self.configs_name:
                    QMessageBox.warning(self, "输入错误", "配置重复，请修改配置名称！")
                    self.lineEdit_ConfigName.setFocus()  # 聚焦到输入框重新输入
                    return
            self.config.config_name = config_name

        if not tester_logical_address:
            QMessageBox.warning(self, "输入错误", "Tester逻辑地址不能为空！")
            self.lineEdit_TesterLogicalAddress.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = tester_logical_address.strip()
            try:
                self.config.tester_logical_address = hex_str_to_int(text)
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
                self.config.dut_logical_address = hex_str_to_int(text)
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
                self.config.dut_ipv4_address = text
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "DUT IP地址输入错误",
                    f"仅支持IPv4地址"
                )
                self.lineEdit_DUT_IP.setFocus()  # 聚焦到输入框重新输入
                return

        if self.checkBox_RouteActive.isChecked():
            self.config.is_routing_activation_use = 1
            try:
                self.config.oem_specific = int(self.lineEdit_OEMSpecific.text())
            except Exception as e:
                logger.exception(e)


        else:
            self.config.is_routing_activation_use = 0

        # 校验通过，关闭对话框
        self.accept()
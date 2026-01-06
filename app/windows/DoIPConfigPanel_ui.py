import ipaddress
import logging
import os
from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QMessageBox, QFileDialog, QCheckBox

from app.resources.resources import IconEngine
from app.ui.DoIPConfigUI import Ui_DoIPConfig
from app.user_data import DoIPConfig
from app.utils import hex_str_to_int

logger = logging.getLogger('UDSTool.' + __name__)

# -------------------------- 配置面板类 --------------------------
class DoIPConfigPanel(QDialog, Ui_DoIPConfig):
    """
    配置面板类，继承自 QDialog (窗口行为) 和 Ui_Dialog (界面布局)
    """

    def __init__(self, configs_name: list[str], is_create_new_config: bool = False, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(IconEngine.get_icon('config'))
        self.config: Optional[DoIPConfig] = DoIPConfig(
            config_name='DoIP_config_panel_default',
            tester_logical_address=0x7e2,
            dut_logical_address=0x773,
            dut_ipv4_address='172.16.104.70'
        )
        self.configs_name = configs_name
        self.is_create_new_config = is_create_new_config
        self.is_delete_config = False
        self.is_delete_data = False
        self.buttonBox.accepted.connect(self._on_accept)
        self.pushButton_delete.clicked.connect(self._on_delete_config)
        self.toolButton_GenerateKeyExOptPath.clicked.connect(self._on_select_key_ex_opt_path)
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
    def _on_select_key_ex_opt_path(self):
        """
        弹出文件选择框，并将结果填入 LineEdit
        """
        # getOpenFileName 返回一个元组 (filePath, filter)
        abs_path, _ = QFileDialog.getOpenFileName(
            self,  # 父窗口
            "选择 GenerateKeyExOpt 文件",  # 标题
            "",  # 默认打开路径 (空字符串表示当前目录)
            "DLL Files (*.dll);Python Files (*.py)"  # 文件过滤器，例如 "DLL Files (*.dll);;All Files (*)"
        )

        if abs_path:
            try:
                # 2. 计算相对路径
                # os.getcwd() 获取当前程序运行的工作目录
                # os.path.relpath(目标路径, 基准路径) 计算相对路径
                rel_path = os.path.relpath(abs_path, os.getcwd())

                # 3. 将相对路径填入输入框
                self.lineEdit_GenerateKeyExOptPath.setText(rel_path)

            except ValueError:
                # Windows 特例：如果文件和程序在不同的盘符（例如 C: 和 D:），
                # 无法计算相对路径，此时会报错，我们保留绝对路径作为后备方案。
                self.lineEdit_GenerateKeyExOptPath.setText(abs_path)

    @Slot()
    def _on_accept(self):
        """校验输入（捕获异常）"""
        config_name = self.lineEdit_ConfigName.text()
        tester_logical_address = self.lineEdit_TesterLogicalAddress.text()
        DUT_logical_address = self.lineEdit_DUTLogicalAddress.text()
        DUT_ipv4_address = self.lineEdit_DUT_IP.text()

        if self.is_delete_config:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("删除配置")
            msg_box.setText(f"确认删除配置 {self.lineEdit_ConfigName.text()}")

            # 设置按钮
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            # 添加复选框
            cb = QCheckBox("同时Case等关联数据")
            msg_box.setCheckBox(cb)

            # 4. 显示并获取结果
            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                self.config = None
                if cb.isChecked():
                    self.is_delete_data = True
                self.accept()
                return
            else:
                self.is_delete_config = False
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
                logger.exception(str(e))


        else:
            self.config.is_routing_activation_use = 0

        self.config.GenerateKeyExOptPath = self.lineEdit_GenerateKeyExOptPath.text()

        # 校验通过，关闭对话框
        self.accept()
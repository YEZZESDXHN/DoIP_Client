import logging.config
import sys
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal
from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
                               QSizePolicy, QLayout, QDialog, QHeaderView, QStyle)
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from UI.DoIPConfigPanel_ui import DoIPConfigPanel
from UI.DoIPToolMainUI import Ui_MainWindow
from UDSOnIP import QUDSOnIPClient
from UI.DoIPTraceTable_ui import DoIPTraceTableView
from UI.treeView_ui import DiagTreeView, DiagTreeDataModel
from utils import get_ethernet_ips

# 日志配置
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger('UDSOnIPClient')


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    和 Ui_MainWindow（界面元素定义）。
    """
    connect_or_disconnect_doip_signal = Signal()
    doip_send_raw_payload_signal = Signal(bytes)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 初始化属性
        self._init_attributes()

        # 初始化UI、客户端、信号、IP列表
        self._init_ui()
        self._init_doip_client()
        self._init_signals()
        self._refresh_ip_list()

    def _init_attributes(self):
        """初始化所有配置属性（集中管理，提高可读性）"""
        self.uds_on_ip_client = None
        self.uds_on_ip_client_thread = None

        self.ip_list = []
        self.ecu_ip_address = '172.16.104.70'
        # self.ecu_ip_address = '127.0.0.1'
        self.client_ip_address = None
        self.client_logical_address = 0x7e2
        self.ecu_logical_address = 0x773
        self.vm_specific = 0
        self.tcp_port = TCP_DATA_UNSECURED
        self.udp_port = UDP_DISCOVERY
        self.activation_type = RoutingActivationRequest.ActivationType.Default
        self.protocol_version = 0x02
        self.use_secure = False
        self.auto_reconnect_tcp = True
        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config

    def _init_doip_client(self):
        """初始化DoIP客户端和线程"""
        # 创建线程和客户端实例
        self.uds_on_ip_client_thread = QThread()
        self.uds_on_ip_client = QUDSOnIPClient()

        # 将客户端移到子线程，避免阻塞主线程
        self.uds_on_ip_client.moveToThread(self.uds_on_ip_client_thread)

        # 启动线程
        self.uds_on_ip_client_thread.start()
        logger.info("DoIP客户端线程已启动")

    def _init_ui(self):
        """初始化界面组件属性"""
        icon_disconnected = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.pushButton_ConnectDoIP.setIcon(icon_disconnected)

        # 添加表格
        self.tableView_DoIPTrace = self._add_custom_table_view(self.groupBox_DoIPTrace)

        # 添加DoIPTrace表格到诊断自动化流程
        self.tableView_DoIPTrace_Automated_Process = self._add_custom_table_view(self.groupBox_AutomatedDiagTrace)

        # 添加TreeView控件
        self.treeView_Diag = self._add_custom_tree_view(self.scrollArea_DiagTree)

    def _add_custom_tree_view(self, parent_widget):
        """
        在指定控件上添加控件treeView
        :param parent_widget: 父控件
        """
        if not parent_widget:
            logger.error("父控件无效")
            return
        tree_view = DiagTreeView(parent=parent_widget)
        tree_model = DiagTreeDataModel()
        tree_view.setModel(tree_model)
        tree_view.expandAll()  # 展开所有节点
        tree_view.resizeColumnToContents(0)  # 设置第0列显示全部文本，不会截断

        logger.debug(f"父控件：{parent_widget.objectName()}")

        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(tree_view)
        layout.setStretchFactor(tree_view, 1)

        # 设置父控件尺寸策略（确保父控件也铺满上层）
        parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return tree_view


    def _add_custom_table_view(self, parent_widget):
        """
        在指定控件上添加控件custom_table
        :param parent_widget: 父控件
        """
        if not parent_widget:
            logger.error("父控件无效")
            return
        table_view_doip_trace = DoIPTraceTableView(parent=parent_widget)
        logger.debug(f"父控件：{parent_widget.objectName()}")


        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(table_view_doip_trace)
        layout.setStretchFactor(table_view_doip_trace, 1)

        # 设置父控件尺寸策略（确保父控件也铺满上层）
        parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return table_view_doip_trace

    def _init_signals(self):
        """初始化所有信号槽连接（统一管理）"""
        # UI组件信号
        self._connect_ui_signals()

        # DoIP客户端信号
        self._connect_doip_client_signals()

    def _connect_ui_signals(self):
        """连接UI组件的信号到槽函数"""
        # 按钮信号
        self.pushButton_ConnectDoIP.clicked.connect(self.change_doip_connect_state)
        self.pushButton_SendDoIP.clicked.connect(self._get_data_and_send_raw_doip_payload)
        self.pushButton_EditConfig.clicked.connect(self.open_edit_config_panel)
        self.pushButton_RefreshIP.clicked.connect(self.get_ip_list)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.comboBox_TesterIP.currentIndexChanged.connect(self.set_tester_ip)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_doip_signal.connect(self.uds_on_ip_client.change_doip_connect_state)
        self.doip_send_raw_payload_signal.connect(self.uds_on_ip_client.send_payload)

        # treeView双击信号获取触发send_raw_doip_payload发送数据
        self.treeView_Diag.clicked_node_data.connect(self.send_raw_doip_payload)


    def _connect_doip_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_on_ip_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_on_ip_client.doip_connect_state.connect(self._update_doip_connect_state)

        self.uds_on_ip_client.doip_response.connect(self.tableView_DoIPTrace.add_trace_data)
        self.uds_on_ip_client.doip_request.connect(self.tableView_DoIPTrace.add_trace_data)

        self.uds_on_ip_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        self.uds_on_ip_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)

        self.uds_on_ip_client.doip_response.connect(self.doip_response_callback)

    @Slot(dict)
    def doip_response_callback(self, data: dict):
        self.pushButton_SendDoIP.setDisabled(False)


    def set_tester_ip(self, index: int):
        """设置测试机IP"""
        self.client_ip_address = None if index == 0 else self.comboBox_TesterIP.currentText()
        logger.debug(f"测试机IP已设置为：{self.client_ip_address}")

    @Slot()
    def set_auto_reconnect_tcp(self, state):
        """设置TCP自动重连"""
        self.auto_reconnect_tcp = bool(state)
        logger.debug(f"TCP自动重连已设置为：{self.auto_reconnect_tcp}")

    @Slot()
    def _get_data_and_send_raw_doip_payload(self):
        hex_str = self.lineEdit_DoIPRawDate.text().strip()
        if not hex_str:
            logger.warning("发送数据为空，取消发送")
            return
        try:
            byte_data = bytes.fromhex(hex_str)
            self.send_raw_doip_payload(byte_data)
        except ValueError as e:
            logger.error(f"十六进制数据格式错误：{e}，输入内容：{hex_str}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{e}")

    @Slot(bytes)
    def send_raw_doip_payload(self, byte_data: bytes):
        """获通过信号与槽的机制传递给DoIP Client并发送出去"""
        if not byte_data:
            logger.warning("发送数据为空，取消发送")
            return

        try:
            self.doip_send_raw_payload_signal.emit(byte_data)
            self.pushButton_SendDoIP.setDisabled(True)
            logger.debug(f"已发送DoIP数据到传输层：{byte_data.hex()}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{e}")

    def change_doip_connect_state(self):
        """切换DoIP连接状态（连接/断开）"""
        # 更新客户端配置
        self._update_doip_client_config()

        # 禁用按钮防止重复点击
        self.pushButton_ConnectDoIP.setDisabled(True)
        self.connect_or_disconnect_doip_signal.emit()
        logger.debug("已触发DoIP连接状态切换信号")

    def _update_doip_client_config(self) -> None:
        """批量更新DoIP客户端配置"""
        if not self.uds_on_ip_client:
            logger.warning("DoIP客户端未初始化，跳过配置更新")
            return

        client = self.uds_on_ip_client
        client.ecu_ip_address = self.ecu_ip_address
        client.ecu_logical_address = self.ecu_logical_address
        client.tcp_port = self.tcp_port
        client.udp_port = self.udp_port
        client.activation_type = self.activation_type
        client.protocol_version = self.protocol_version
        client.client_logical_address = self.client_logical_address
        client.client_ip_address = self.client_ip_address
        client.use_secure = self.use_secure
        client.auto_reconnect_tcp = self.auto_reconnect_tcp
        client.vm_specific = self.vm_specific
        client.uds_request_timeout = self.uds_request_timeout
        client.uds_config = self.uds_config
        logger.debug("DoIP客户端配置已更新")

    @Slot()
    def open_edit_config_panel(self):
        """打开DoIP配置编辑面板"""
        config_panel = DoIPConfigPanel(parent=self)

        # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
        config_panel.lineEdit_DUT_IP.setText(self.ecu_ip_address)
        config_panel.lineEdit_TesterLogicalAddress.setText(f"{self.client_logical_address:X}")
        config_panel.lineEdit_DUTLogicalAddress.setText(f"{self.ecu_logical_address:X}")

        if config_panel.exec() == QDialog.Accepted:
            self.client_logical_address = config_panel.config.get('tester_logical_address', self.client_logical_address)
            self.ecu_logical_address = config_panel.config.get('DUT_logical_address', self.ecu_logical_address)
            self.ecu_ip_address = config_panel.config.get('DUT_ipv4_address', self.ecu_ip_address).strip()
            logger.info(
                f"DoIP配置已更新 - 测试机逻辑地址: 0x{self.client_logical_address:X}, "
                f"ECU逻辑地址: 0x{self.ecu_logical_address:X}, ECU IP: {self.ecu_ip_address}"
            )

    @Slot(bool)
    def _update_doip_connect_state(self, state: bool):
        """更新DoIP连接状态的UI显示"""
        self.pushButton_ConnectDoIP.setDisabled(False)

        icon_connected = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        icon_disconnected = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)

        icon = icon_connected if state else icon_disconnected
        btn_text = '已连接' if state else '连接'
        self.pushButton_ConnectDoIP.setText(btn_text)
        self.pushButton_ConnectDoIP.setIcon(icon)
        logger.info(f"DoIP连接状态已更新为：{btn_text}")

    @Slot()
    def get_ip_list(self):
        """获取本地IP列表"""
        try:
            ethernet_ips = get_ethernet_ips()
            self.ip_list = [('Auto', '')] + list(ethernet_ips.items())
            self._update_ip_combobox()
            logger.debug(f"已获取本地IP列表，共{len(self.ip_list) - 1}个可用IP")
        except Exception as e:
            logger.error(f"获取IP列表失败：{e}")

    def _refresh_ip_list(self) -> None:
        """刷新本地IP列表到下拉框"""
        self.get_ip_list()  # 复用get_ip_list方法，减少冗余

    def _update_ip_combobox(self):
        """更新IP下拉框"""
        self.comboBox_TesterIP.clear()
        self.comboBox_TesterIP.addItem('Auto')
        for _, ip in self.ip_list[1:]:  # 跳过Auto选项
            self.comboBox_TesterIP.addItem(ip)

    def closeEvent(self, event) -> None:
        """重写关闭事件，优雅退出线程"""
        # 停止DoIP客户端线程
        if self.uds_on_ip_client_thread:
            self.uds_on_ip_client_thread.quit()
            if self.uds_on_ip_client_thread.wait(3000):  # 等待3秒超时
                logger.info("DoIP客户端线程已正常停止")
            else:
                logger.warning("DoIP客户端线程强制退出")

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
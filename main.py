import logging.config
import sys
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal
from PySide6.QtWidgets import QMainWindow, QApplication, QTableView, QScrollBar
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from ui_custom import DoIPConfigPanel, DoIPTraceTableModel
from DoIPToolMainUI import Ui_MainWindow
from UDSOnIP import QUDSOnIPClient
from utils import get_ethernet_ips

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

        # 1. 调用生成的 setupUi 方法
        # 这将初始化所有界面元素（按钮、标签等）
        self.uds_on_ip_client = None
        self.uds_on_ip_client_thread = None
        self.setupUi(self)
        self.ip_list = []
        self.ecu_ip_address = '172.16.104.70'
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

        # 自动滚动开关：默认开启（显示最新数据）
        self._auto_scroll: bool = True

        self._init_ui()
        self._init_doip_client()
        self._init_signals()
        self._refresh_ip_list()


    def _init_doip_client(self):
        """初始化DoIP客户端和线程"""
        # 创建线程和客户端实例
        self.uds_on_ip_client_thread = QThread()
        self.uds_on_ip_client = QUDSOnIPClient()

        # 将客户端移到子线程，避免阻塞主线程
        self.uds_on_ip_client.moveToThread(self.uds_on_ip_client_thread)

        # 启动线程
        self.uds_on_ip_client_thread.start()

    def _init_ui(self):
        """初始化界面组件属性"""
        # 设置表格属性：整行选中、隔行变色、允许排序
        trace_table = self.tableView_DoIPTrace
        trace_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        trace_table.setAlternatingRowColors(True)
        # trace_table.setSortingEnabled(True)

        # 初始化表格模型
        self.trace_model = DoIPTraceTableModel()
        trace_table.setModel(self.trace_model)

        # 绑定表格滚动条的信号，监听滚动状态
        self._bind_scroll_listener()


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
        self.pushButton_SendDoIP.clicked.connect(self.send_raw_doip_payload)
        self.pushButton_EditConfig.clicked.connect(self.open_edit_config_panel)
        self.pushButton_RefreshIP.clicked.connect(self.get_ip_list)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.comboBox_TesterIP.currentIndexChanged.connect(self.set_tester_ip)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_doip_signal.connect(self.uds_on_ip_client.change_doip_connect_state)
        self.doip_send_raw_payload_signal.connect(self.uds_on_ip_client.send_payload)

    def _connect_doip_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_on_ip_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_on_ip_client.doip_connect_state.connect(self._update_doip_connect_state)
        self.uds_on_ip_client.doip_response.connect(self._add_doip_trace_data)

    def set_tester_ip(self, index: int):
        if index == 0:
            self.client_ip_address = None
        else:
            self.client_ip_address = self.comboBox_TesterIP.currentText()
    @Slot()
    def set_auto_reconnect_tcp(self, state):
        if state:
            self.auto_reconnect_tcp = True
        else:
            self.auto_reconnect_tcp = False

    # 获取发送数据窗口的hex,转换为bytes，通过信号与槽的机制传递给DoIP Client并发送出去
    @Slot()
    def send_raw_doip_payload(self):
        hex_str = self.lineEdit_DoIPRawDate.text()
        if hex_str:
            try:
                byte_data = bytes.fromhex(hex_str)
                self.doip_send_raw_payload_signal.emit(byte_data)
            except Exception as e:
                logger.exception(e)
        else:
            logger.warning("未输入数据")

    # 【新增】绑定表格滚动条的监听事件
    def _bind_scroll_listener(self) -> None:
        """绑定表格滚动条的信号，监听用户的滚动操作"""
        scroll_bar: QScrollBar = self.tableView_DoIPTrace.verticalScrollBar()
        # 滚动条数值变化时触发（用户手动滚动或自动滚动）
        scroll_bar.valueChanged.connect(self._on_scroll_value_changed)

    # 【新增】滚动条数值变化的回调
    def _on_scroll_value_changed(self, value: int) -> None:
        """根据滚动条位置更新自动滚动开关状态"""
        scroll_bar: QScrollBar = self.tableView_DoIPTrace.verticalScrollBar()
        max_value = scroll_bar.maximum()
        # 若滚动到最底部（最新数据），开启自动滚动；否则关闭
        self._auto_scroll = (value == max_value)
        if self._auto_scroll:
            logger.debug("表格滚动到最底部，开启自动滚动")
        else:
            logger.debug("用户滚动到旧数据，关闭自动滚动")

    # 【新增】判断是否滚动到表格底部
    def _is_scrolled_to_bottom(self) -> bool:
        """检查表格是否滚动到最底部"""
        scroll_bar: QScrollBar = self.tableView_DoIPTrace.verticalScrollBar()
        return scroll_bar.value() == scroll_bar.maximum()

    # 【新增】强制滚动到表格底部
    def _scroll_to_bottom(self) -> None:
        """强制将表格滚动到最后一行（最新数据）"""
        if not self.trace_model:
            return
        # 获取模型的最后一行索引
        last_row = self.trace_model.rowCount() - 1
        if last_row < 0:
            return
        # 滚动到最后一行
        self.tableView_DoIPTrace.scrollToBottom()


    def change_doip_connect_state(self):
        """切换DoIP连接状态（连接/断开）"""
        # 更新客户端配置
        self._update_doip_client_config()

        # 禁用按钮防止重复点击
        self.pushButton_ConnectDoIP.setDisabled(True)

        self.connect_or_disconnect_doip_signal.emit()

    def _update_doip_client_config(self) -> None:
        """批量更新DoIP客户端配置"""
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

    @Slot()
    def open_edit_config_panel(self):
        """打开DoIP配置编辑面板"""
        config_panel = DoIPConfigPanel(parent=self)

        # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
        config_panel.lineEdit_DUT_IP.setText(self.ecu_ip_address)
        config_panel.lineEdit_TesterLogicalAddress.setText(
            f"{self.client_logical_address:X}"
        )
        config_panel.lineEdit_DUTLogicalAddress.setText(
            f"{self.ecu_logical_address:X}"
        )

        # 连接配置确认信号
        config_panel.config_signal.connect(self.update_doip_config)
        config_panel.exec()

    @Slot()
    def update_doip_config(self, config):
        """更新DoIP配置（从配置面板接收）"""
        try:
            # 类型转换和校验
            self.client_logical_address = config.get('tester_logical_address', '')
            self.ecu_logical_address = config.get('DUT_logical_address', '')
            self.ecu_ip_address = config.get('DUT_ipv4_address', self.ecu_ip_address).strip()

            logger.info(
                f"DoIP配置已更新 - 测试机逻辑地址: 0x{self.client_logical_address:X}, "
                f"ECU逻辑地址: 0x{self.ecu_logical_address:X}, ECU IP: {self.ecu_ip_address}"
            )
        except (ValueError, KeyError) as e:
            logger.error(f"更新DoIP配置失败: {e}，配置数据: {config}")



    def _add_doip_trace_data(self, data: list) -> None:
        """添加DoIP追踪数据到表格模型"""
        if self.trace_model:
            self.trace_model.append_trace_data(data)
            # 若自动滚动开关开启，添加新数据后滚动到底部
            if self._auto_scroll:
                self._scroll_to_bottom()
        else:
            logger.warning("追踪表格模型未初始化，无法添加数据")

    def _update_doip_connect_state(self, state: bool):
        """更新DoIP连接状态的UI显示"""
        # 重新启用按钮
        self.pushButton_ConnectDoIP.setDisabled(False)
        if state:
            self.pushButton_ConnectDoIP.setText('已连接')
        else:
            self.pushButton_ConnectDoIP.setText('连接')

    @Slot()
    def get_ip_list(self):
        ethernet_ips = get_ethernet_ips()
        self.ip_list.clear()
        self.ip_list.append(('Auto', ''))
        _ip_list = list(ethernet_ips.items())
        self.ip_list.extend(_ip_list)

        self.comboBox_TesterIP.clear()
        self.comboBox_TesterIP.addItem('Auto')
        for ip in _ip_list:
            self.comboBox_TesterIP.addItem(ip[1])

    def _refresh_ip_list(self) -> None:
        """刷新本地IP列表到下拉框"""
        try:
            ethernet_ips = get_ethernet_ips()
            self.ip_list = [('Auto', '')]
            self.ip_list.extend(list(ethernet_ips.items()))

            # 更新下拉框
            self.comboBox_TesterIP.clear()
            self.comboBox_TesterIP.addItem('Auto')

            for _, ip in self.ip_list:  # 跳过Auto选项
                self.comboBox_TesterIP.addItem(ip)

            logger.debug(f"已刷新IP列表，共找到 {len(self.ip_list) - 1} 个以太网IP")
        except Exception as e:
            logger.error(f"刷新IP列表失败: {e}")

    def closeEvent(self, event) -> None:
        """重写关闭事件，优雅退出线程"""
        # 停止DoIP客户端线程
        if self.uds_on_ip_client_thread:
            self.uds_on_ip_client_thread.quit()
            self.uds_on_ip_client_thread.wait(3000)  # 等待3秒超时
            logger.info("DoIP客户端线程已停止")

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon('icon.ico'))
    # app.setApplicationName('CAN tool')
    app.setStyle("WindowsVista")
    w = MainWindow()
    # w.setWindowTitle("CAN tool " + current_version)
    # w.setWindowIcon(QIcon('icon.ico'))

    w.show()
    sys.exit(app.exec())

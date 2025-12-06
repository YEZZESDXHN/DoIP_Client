import logging.config
import sys
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal, Qt
from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
                               QSizePolicy, QDialog, QStyle, QAbstractItemView)
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from UI.AutomaticDiagnosisProcess_ui import DiagProcessTableView, DiagProcessTableModel
from UI.DoIPConfigPanel_ui import DoIPConfigPanel
from UI.DoIPToolMainUI import Ui_MainWindow
from UDSOnIP import QUDSOnIPClient
from UI.DoIPTraceTable_ui import DoIPTraceTableView
from UI.sql_data_panel import SQLTablePanel
from UI.treeView_ui import DiagTreeView, DiagTreeDataModel
from db_manager import DBManager
from user_data import DoIPConfig, TableViewData
from utils import get_ethernet_ips
from pathlib import Path

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

        self.tester_ip_address: Optional[str] = None
        self.current_doip_config: Optional[DoIPConfig] = None
        self.db_manager: Optional[DBManager] = None
        self.uds_on_ip_client = None
        self.uds_on_ip_client_thread = None
        self.auto_reconnect_tcp = True
        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config

        self.ip_list = []

        self.db_path = 'Database/database.db'
        self.init_database(self.db_path)
        self._init_current_doip_config()

        # 初始化UI、客户端、信号、IP列表
        self._init_ui()
        self._init_doip_client()
        self._init_signals()
        self._refresh_ip_list()

    def _init_current_doip_config(self):
        try:
            current_config_name = self.db_manager.get_active_config_name()
            self.current_doip_config = self.db_manager.query_doip_config(current_config_name)
        except Exception as e:
            logger.exception(f'{e}')

            self.current_doip_config = DoIPConfig(
                config_name='default',
                tester_logical_address=0x7e2,
                dut_logical_address=0x773,
                dut_ipv4_address='172.16.104.70',
            )

    def init_database(self, db):
        db_path = Path(db)  # 转换为 Path 对象（方便处理路径）
        db_dir = db_path.parent  # 获取数据库文件所在的文件夹路径

        # 如果文件夹不存在，创建文件夹
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)  # parents=True：创建多级目录；exist_ok=True：已存在则不报错
                logger.info(f"数据库文件夹不存在，已自动创建：{db_dir}")
            except Exception as e:
                logger.exception(f"创建数据库文件夹失败：{str(e)}")
        self.db_manager = DBManager(db)



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

        # 共用同一数据模型，需要取消以下两个信号连接
        # self.uds_on_ip_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_on_ip_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # 搜索关键字可以在_connect_doip_client_signals中可以找到
        self.tableView_DoIPTrace_Automated_Process.trace_model = self.tableView_DoIPTrace.trace_model
        self.tableView_DoIPTrace_Automated_Process.setModel(self.tableView_DoIPTrace.trace_model)


        # 添加TreeView控件
        self.treeView_Diag = self._add_custom_tree_view(self.scrollArea_DiagTree)
        self.treeView_Diag_Process = self._add_custom_tree_view(self.scrollArea_DiagTreeForProcess)
        self.treeView_Diag_Process.setModel(self.treeView_Diag.model())
        self.treeView_Diag_Process.expandAll()
        self.treeView_Diag_Process.setDragEnabled(True)  # 允许拖拽
        self.treeView_Diag_Process.setDragDropMode(QAbstractItemView.DragOnly)  # 仅作为拖拽源
        self.treeView_Diag_Process.setDefaultDropAction(Qt.CopyAction)

        self.diag_process_table_view = self._add_diag_process_table_view(self.groupBox_AutomatedDiagProcessTable)


        doip_config_names = self.db_manager.get_all_config_names()
        if self.current_doip_config.config_name in doip_config_names:
            for config in doip_config_names:
                self.comboBox_ChooseConfig.addItem(config)
            self.comboBox_ChooseConfig.setCurrentText(self.current_doip_config.config_name)


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

    def _add_diag_process_table_view(self, parent_widget):
        if not parent_widget:
            logger.error("父控件无效")
            return
        diag_process_table_view = DiagProcessTableView(parent=parent_widget)
        diag_process_table_model = DiagProcessTableModel()
        diag_process_table_view.setModel(diag_process_table_model)
        logger.debug(f"父控件：{parent_widget.objectName()}")


        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(diag_process_table_view)
        layout.setStretchFactor(diag_process_table_view, 1)

        # 设置父控件尺寸策略（确保父控件也铺满上层）
        parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return diag_process_table_view


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
        self.pushButton_CreateConfig.clicked.connect(self.open_create_config_panel)
        self.pushButton_RefreshIP.clicked.connect(self.get_ip_list)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.comboBox_TesterIP.currentIndexChanged.connect(self.set_tester_ip)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_doip_signal.connect(self.uds_on_ip_client.change_doip_connect_state)
        self.doip_send_raw_payload_signal.connect(self.uds_on_ip_client.send_payload)

        # treeView双击信号获取触发send_raw_doip_payload发送数据
        self.treeView_Diag.clicked_node_data.connect(self.send_raw_doip_payload)

        self.action_database.triggered.connect(self.open_sql_ui)

        self.comboBox_ChooseConfig.currentIndexChanged.connect(self._on_doip_config_chaneged)


    def _connect_doip_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_on_ip_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_on_ip_client.doip_connect_state.connect(self._update_doip_connect_state)

        self.uds_on_ip_client.doip_response.connect(self.tableView_DoIPTrace.add_trace_data)
        self.uds_on_ip_client.doip_request.connect(self.tableView_DoIPTrace.add_trace_data)

        # self.uds_on_ip_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_on_ip_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)

        self.uds_on_ip_client.doip_response.connect(self.doip_response_callback)

    @Slot(dict)
    def doip_response_callback(self, data: TableViewData):
        self.pushButton_SendDoIP.setDisabled(False)

    @Slot(int)
    def _on_doip_config_chaneged(self, index: int):
        config_name = self.comboBox_ChooseConfig.currentText()
        self.current_doip_config = self.db_manager.query_doip_config(config_name)
        self.db_manager.set_active_config(config_name)

    def set_tester_ip(self, index: int):
        """设置测试机IP"""
        self.tester_ip_address = None if index == 0 else self.comboBox_TesterIP.currentText()
        logger.debug(f"测试机IP已设置为：{self.tester_ip_address}")

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
        client.ecu_ip_address = self.current_doip_config.dut_ipv4_address
        client.ecu_logical_address = self.current_doip_config.dut_logical_address
        client.tcp_port = self.current_doip_config.tcp_port
        client.udp_port = self.current_doip_config.udp_port
        client.activation_type = self.current_doip_config.activation_type
        client.protocol_version = self.current_doip_config.protocol_version
        client.client_logical_address = self.current_doip_config.tester_logical_address
        client.client_ip_address = self.tester_ip_address
        client.use_secure = self.current_doip_config.use_secure
        client.auto_reconnect_tcp = self.auto_reconnect_tcp
        client.vm_specific = self.current_doip_config.oem_specific
        client.uds_request_timeout = self.uds_request_timeout
        client.uds_config = self.uds_config
        logger.debug("DoIP客户端配置已更新")

    @Slot()
    def open_sql_ui(self):
        """
        打开sql可视化窗口
        """
        self.sql_table_panel = SQLTablePanel(self.db_path)
        self.sql_table_panel.show()

    @Slot()
    def open_create_config_panel(self):
        """打开DoIP新建配置面板"""
        config_panel = DoIPConfigPanel(parent=self, is_create_new_config=True)
        config_panel.setWindowTitle('新建配置')
        new_config = DoIPConfig()

        # config_panel.lineEdit_ConfigName.setText(self.db_manager.get_active_config_name())
        # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
        config_panel.lineEdit_DUT_IP.setText(new_config.dut_ipv4_address)
        config_panel.lineEdit_TesterLogicalAddress.setText(f"{new_config.tester_logical_address:X}")
        config_panel.lineEdit_DUTLogicalAddress.setText(f"{new_config.dut_logical_address:X}")
        config_panel.lineEdit_OEMSpecific.setText(str(new_config.oem_specific))
        config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Checked)

        if config_panel.exec() == QDialog.Accepted:
            new_config.config_name = config_panel.config.config_name
            new_config.tester_logical_address = config_panel.config.tester_logical_address
            new_config.dut_logical_address = config_panel.config.dut_logical_address
            new_config.dut_ipv4_address = config_panel.config.dut_ipv4_address
            new_config.is_routing_activation_use = config_panel.config.is_routing_activation_use
            new_config.oem_specific = config_panel.config.oem_specific
            logger.info(
                f"新DoIP配置 - 测试机逻辑地址: 0x{config_panel.config.tester_logical_address:X}, "
                f"ECU逻辑地址: 0x{config_panel.config.dut_logical_address:X}, ECU IP: {config_panel.config.dut_ipv4_address}"
            )
            self.db_manager.add_doip_config(new_config)
            self.comboBox_ChooseConfig.addItem(new_config.config_name)

    @Slot()
    def open_edit_config_panel(self):
        """打开DoIP配置编辑面板"""
        config_panel = DoIPConfigPanel(parent=self)
        config_panel.setWindowTitle('修改配置')
        config_panel.lineEdit_ConfigName.setText(self.db_manager.get_active_config_name())
        # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
        config_panel.lineEdit_DUT_IP.setText(self.current_doip_config.dut_ipv4_address)
        config_panel.lineEdit_TesterLogicalAddress.setText(f"{self.current_doip_config.tester_logical_address:X}")
        config_panel.lineEdit_DUTLogicalAddress.setText(f"{self.current_doip_config.dut_logical_address:X}")
        config_panel.lineEdit_OEMSpecific.setText(str(self.current_doip_config.oem_specific))
        if self.current_doip_config.is_routing_activation_use:
            config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Checked)
        else:
            config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Unchecked)

        if config_panel.exec() == QDialog.Accepted:
            if config_panel.config is None:  # 删除配置
                self.db_manager.delete_doip_config(self.current_doip_config.config_name)
                doip_config_names = self.db_manager.get_all_config_names()
                if len(doip_config_names) > 0:
                    try:
                        self.comboBox_ChooseConfig.clear()
                        self.db_manager.set_active_config(doip_config_names[0])
                        for config in doip_config_names:
                            self.comboBox_ChooseConfig.addItem(config)
                        self.comboBox_ChooseConfig.setCurrentText(self.current_doip_config.config_name)
                    except Exception as e:
                        self.db_manager.set_active_config('')
                        logger.exception(e)
                else:
                    self.comboBox_ChooseConfig.clear()
            elif isinstance(config_panel.config, DoIPConfig):
                self.current_doip_config.config_name = config_panel.config.config_name
                self.current_doip_config.tester_logical_address = config_panel.config.tester_logical_address
                self.current_doip_config.dut_logical_address = config_panel.config.dut_logical_address
                self.current_doip_config.dut_ipv4_address = config_panel.config.dut_ipv4_address
                self.current_doip_config.is_routing_activation_use = config_panel.config.is_routing_activation_use
                self.current_doip_config.oem_specific = config_panel.config.oem_specific
                self.db_manager.update_doip_config(self.current_doip_config)
                logger.info(
                    f"DoIP配置已更新 - 测试机逻辑地址: 0x{config_panel.config.tester_logical_address:X}, "
                    f"ECU逻辑地址: 0x{config_panel.config.dut_logical_address:X}, ECU IP: {config_panel.config.dut_ipv4_address}"
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
import logging.config
import os
import sys
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal, Qt
from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
                               QSizePolicy, QDialog, QStyle, QAbstractItemView, QFileDialog)
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from UI.AutomaticDiagnosisProcess_ui import DiagProcessTableView, DiagProcessTableModel, DiagProcessCaseTreeView
from UI.DoIPConfigPanel_ui import DoIPConfigPanel
from UI.DoIPToolMainUI import Ui_MainWindow
from UDSClient import QUDSClient
from UI.DoIPTraceTable_ui import DoIPTraceTableView
from UI.sql_data_panel import SQLTablePanel
from UI.UdsServicesTreeView_ui import UdsServicesTreeView, UdsServicesModel
from db_manager import DBManager
from user_data import DoIPConfig, DoIPMessageStruct, UdsService
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
        self.uds_client: Optional[QUDSClient] = None
        self.uds_client_thread = None
        self.auto_reconnect_tcp = True
        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config
        self.external_script_path: str = ''

        self.ip_list = []

        self.db_path = 'Database/database.db'
        self.init_database(self.db_path)
        self.uds_services: UdsService = UdsService()
        self._init_current_doip_config()

        self.add_external_lib()

        # 初始化UI、客户端、信号、IP列表
        self._init_ui()
        self._init_doip_client()
        self._init_signals()
        self._refresh_ip_list()
        self.status_bar = self.statusBar()

    def add_external_lib(self):
        # ExternalLib sys.path
        lib_dir = os.path.dirname(os.path.abspath('ExternalLib'))
        if lib_dir not in sys.path:
            sys.path.append(lib_dir)

    def _init_current_doip_config(self):
        try:
            current_config_name = self.db_manager.get_active_config_name()
            self.current_doip_config = self.db_manager.query_doip_config(current_config_name)
        except Exception as e:
            logger.exception(f'{str(e)}')

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

    @Slot(str)
    def status_bar_show_message(self, msg: str):
        self.status_bar.showMessage(msg, 0)

    def _init_doip_client(self):
        """初始化DoIP客户端和线程"""
        # 创建线程和客户端实例
        self.uds_client_thread = QThread()
        self.uds_client = QUDSClient()

        # 将客户端移到子线程，避免阻塞主线程
        self.uds_client.moveToThread(self.uds_client_thread)

        # 启动线程
        self.uds_client_thread.start()
        logger.info("DoIP客户端线程已启动")

    def _init_ui(self):
        """初始化界面组件属性"""
        self.splitter_3.setStretchFactor(0, 1)
        self.splitter_3.setStretchFactor(1, 5)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 5)

        icon_disconnected = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.pushButton_ConnectDoIP.setIcon(icon_disconnected)

        # 添加表格
        self.tableView_DoIPTrace = self._add_custom_table_view(self.groupBox_DoIPTrace)

        # 添加DoIPTrace表格到诊断自动化流程
        self.tableView_DoIPTrace_Automated_Process = self._add_custom_table_view(self.groupBox_AutomatedDiagTrace)

        # 共用同一数据模型，需要取消以下两个信号连接
        # self.uds_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # 搜索关键字可以在_connect_doip_client_signals中可以找到
        self.tableView_DoIPTrace_Automated_Process.trace_model = self.tableView_DoIPTrace.trace_model
        self.tableView_DoIPTrace_Automated_Process.setModel(self.tableView_DoIPTrace.trace_model)

        self.uds_services.update_from_json(self.db_manager.get_services_json(self.current_doip_config.config_name))
        # 添加TreeView控件
        self.treeView_DoIPTraceService = self._add_custom_tree_view(self.scrollArea_DiagTree)
        self.treeView_Diag_Process = self._add_custom_tree_view(self.scrollArea_DiagTreeForProcess)
        self.treeView_Diag_Process.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.treeView_Diag_Process.setModel(self.treeView_DoIPTraceService.model())
        self.treeView_Diag_Process.expandAll()
        self.treeView_Diag_Process.setDragEnabled(True)  # 允许拖拽
        self.treeView_Diag_Process.setDragDropMode(QAbstractItemView.DragOnly)  # 仅作为拖拽源
        self.treeView_Diag_Process.setDefaultDropAction(Qt.CopyAction)

        self.diag_process_table_view = self._add_diag_process_table_view(self.groupBox_AutomatedDiagProcessTable)

        self.treeView_uds_case = self._add_uds_case_tree_view(self.scrollArea_UdsCaseTree)

        doip_config_names = self.db_manager.get_all_config_names()
        if self.current_doip_config.config_name in doip_config_names:
            for config in doip_config_names:
                self.comboBox_ChooseConfig.addItem(config)
            self.comboBox_ChooseConfig.setCurrentText(self.current_doip_config.config_name)

        self.treeView_uds_case.clicked_case_id.connect(self.diag_process_table_view.model.get_case_step_from_db)

    @Slot()
    def _save_services_to_db(self):
        self.db_manager.add_services_config(self.current_doip_config.config_name, self.uds_services.to_json())

    def _add_uds_case_tree_view(self, parent_widget):
        if not parent_widget:
            logger.error("父控件无效")
            return
        tree_view = DiagProcessCaseTreeView(parent=parent_widget, db_manager=self.db_manager)

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

    def _add_custom_tree_view(self, parent_widget):
        """
        在指定控件上添加控件treeView
        :param parent_widget: 父控件
        """
        if not parent_widget:
            logger.error("父控件无效")
            return
        tree_view = UdsServicesTreeView(parent=parent_widget, uds_service=self.uds_services)

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
        diag_process_table_view = DiagProcessTableView(parent=parent_widget, db_manager=self.db_manager)
        # diag_process_table_model = DiagProcessTableModel()
        # diag_process_table_view.setModel(diag_process_table_model)
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

        self.toolButton_LoadExternalScript.clicked.connect(self.choose_external_script)
        self.toolButton_LoadExternalScript.clicked.connect(self.uds_client.load_external_script)
        self.pushButton_ExternalScriptRun.clicked.connect(self.uds_client.run_external_script)
        self.pushButton_ExternalScriptStop.clicked.connect(self.uds_client.stop_external_script)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.comboBox_TesterIP.currentIndexChanged.connect(self.set_tester_ip)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_doip_signal.connect(self.uds_client.change_doip_connect_state)
        self.doip_send_raw_payload_signal.connect(self.uds_client.send_payload)

        # treeView双击信号获取触发send_raw_doip_payload发送数据
        self.treeView_DoIPTraceService.clicked_node_data.connect(self.send_raw_doip_payload)

        self.action_database.triggered.connect(self.open_sql_ui)

        self.comboBox_ChooseConfig.currentIndexChanged.connect(self._on_doip_config_chaneged)

        self.treeView_DoIPTraceService.status_bar_message.connect(self.status_bar_show_message)
        self.treeView_DoIPTraceService.data_change_signal.connect(self._save_services_to_db)
        self.treeView_Diag_Process.status_bar_message.connect(self.status_bar_show_message)

    def choose_external_script(self):
        abs_path, _ = QFileDialog.getOpenFileName(
            self,  # 父窗口
            "选择外部Python脚本",  # 标题
            "",  # 默认打开路径 (空字符串表示当前目录)
            "Python Files (*.py)"  # 文件过滤器，例如 "DLL Files (*.dll);;All Files (*)"
        )

        if abs_path:
            try:
                # 2. 计算相对路径
                # os.getcwd() 获取当前程序运行的工作目录
                # os.path.relpath(目标路径, 基准路径) 计算相对路径
                rel_path = os.path.relpath(abs_path, os.getcwd())

                # 3. 将相对路径填入输入框
                self.external_script_path = rel_path


            except ValueError:
                # Windows 特例：如果文件和程序在不同的盘符（例如 C: 和 D:），
                # 无法计算相对路径，此时会报错，我们保留绝对路径作为后备方案。
                self.external_script_path = abs_path
            self.lineEdit_ExternalScriptPath.setText(self.external_script_path)
            self.uds_client.external_script_path = self.external_script_path

    def _connect_doip_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_client.doip_connect_state.connect(self._update_doip_connect_state)

        self.uds_client.doip_response.connect(self.tableView_DoIPTrace.add_trace_data)
        self.uds_client.doip_request.connect(self.tableView_DoIPTrace.add_trace_data)

        # self.uds_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)

        self.uds_client.doip_response.connect(self.doip_response_callback)

    @Slot(dict)
    def doip_response_callback(self, data: DoIPMessageStruct):
        self.pushButton_SendDoIP.setDisabled(False)

    @Slot(int)
    def _on_doip_config_chaneged(self, index: int):
        config_name = self.comboBox_ChooseConfig.currentText()
        self.current_doip_config = self.db_manager.query_doip_config(config_name)
        self.db_manager.set_active_config(config_name)
        self.db_manager.init_services_database()
        self.uds_services.update_from_json(self.db_manager.get_services_json(self.current_doip_config.config_name))
        self.treeView_DoIPTraceService.load_uds_service_to_tree_nodes()
        self.treeView_Diag_Process.expandAll()
        self.treeView_uds_case.refresh()
        self.diag_process_table_view.clear()

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
            logger.error(f"十六进制数据格式错误：{str(e)}，输入内容：{hex_str}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{str(e)}")

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
            logger.exception(f"发送DoIP数据失败：{str(e)}")

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
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，跳过配置更新")
            return

        client = self.uds_client
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
        client.GenerateKeyExOptPath = self.current_doip_config.GenerateKeyExOptPath
        # client.GenerateKeyExOptPath = 'GenerateKeyExOpt/GenerateKeyExOptDemo.py'
        client.uds_request_timeout = self.uds_request_timeout
        client.uds_config = self.uds_config

        client.load_generate_key_ex_opt(client.GenerateKeyExOptPath)

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
        config_panel.lineEdit_GenerateKeyExOptPath.setText(str(self.current_doip_config.GenerateKeyExOptPath))
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
                        logger.exception(str(e))
                else:
                    self.comboBox_ChooseConfig.clear()
            elif isinstance(config_panel.config, DoIPConfig):
                self.current_doip_config.config_name = config_panel.config.config_name
                self.current_doip_config.tester_logical_address = config_panel.config.tester_logical_address
                self.current_doip_config.dut_logical_address = config_panel.config.dut_logical_address
                self.current_doip_config.dut_ipv4_address = config_panel.config.dut_ipv4_address
                self.current_doip_config.is_routing_activation_use = config_panel.config.is_routing_activation_use
                self.current_doip_config.oem_specific = config_panel.config.oem_specific
                self.current_doip_config.GenerateKeyExOptPath = config_panel.config.GenerateKeyExOptPath
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
            logger.error(f"获取IP列表失败：{str(e)}")

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
        if self.uds_client_thread:
            self.uds_client_thread.quit()
            if self.uds_client_thread.wait(3000):  # 等待3秒超时
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
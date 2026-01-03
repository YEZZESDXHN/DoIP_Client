import logging.config
import os
import sys
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
                               QSizePolicy, QDialog, QStyle, QAbstractItemView, QFileDialog, QWidget, QVBoxLayout,
                               QSpacerItem)
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from UI.AutomaticDiagnosisProcess_ui import DiagProcessTableView, DiagProcessCaseTreeView
from UI.DoIPConfigPanel_ui import DoIPConfigPanel
from UI.FlashConfigPanel import FlashConfig, FlashConfigPanel, FlashChooseFileControl, flash_file_block_var_suffix
from UI.UDSToolMainUI import Ui_UDSToolMainWindow
from UDSClient import QUDSClient
from UI.DoIPTraceTable_ui import DoIPTraceTableView
from UI.sql_data_panel import SQLTablePanel
from UI.UdsServicesTreeView_ui import UdsServicesTreeView
from db_manager import DBManager
from external_scripts_executor import QExternalScriptsExecutor
from flash_executor import QFlashExecutor
from global_variables import gFlashVars, FlashFileVars
from user_data import DoIPConfig, DoIPMessageStruct, UdsService
from utils import get_ethernet_ips
from pathlib import Path

# 日志配置
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger('UDSTool')


class MainWindow(QMainWindow, Ui_UDSToolMainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    和 Ui_MainWindow（界面元素定义）。
    """
    connect_or_disconnect_uds_signal = Signal()
    uds_send_raw_payload_signal = Signal(bytes)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        empty_title = QWidget()
        self.dockWidget.setTitleBarWidget(empty_title)

        self.tester_ip_address: Optional[str] = None
        self.current_uds_config: Optional[DoIPConfig] = None
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
        self._init_current_uds_config()

        self.add_external_lib()

        self.flash_config: Optional[FlashConfig] = self.db_manager.load_flash_config(
            self.current_uds_config.config_name)
        if not self.flash_config:
            self.flash_config = FlashConfig()
        self.flash_file_paths = {}
        self.flash_choose_file_controls = {}

        # 初始化UI、客户端、信号、IP列表
        self._init_ui()
        self._init_uds_client()
        self._init_external_scripts_thread()
        self._init_flash_thread()
        self._init_signals()
        self._refresh_ip_list()
        self.status_bar = self.statusBar()




    def add_external_lib(self):
        # ExternalLib sys.path
        lib_dir = os.path.dirname(os.path.abspath('ExternalLib'))
        if lib_dir not in sys.path:
            sys.path.append(lib_dir)

    def _init_current_uds_config(self):
        try:
            current_config_name = self.db_manager.get_active_config_name()
            self.current_uds_config = self.db_manager.query_doip_config(current_config_name)
            if not self.current_uds_config:
                doip_config_names = self.db_manager.get_all_config_names()
                if len(doip_config_names) > 0:
                    try:
                        self.comboBox_ChooseConfig.clear()
                        self.db_manager.set_active_config(doip_config_names[0])
                        for config in doip_config_names:
                            self.comboBox_ChooseConfig.addItem(config)
                        self.comboBox_ChooseConfig.setCurrentText(self.current_uds_config.config_name)
                        self.current_uds_config = self.db_manager.query_doip_config(current_config_name)
                    except Exception as e:
                        self.db_manager.set_active_config('')
                        logger.exception(str(e))
                else:
                    self.comboBox_ChooseConfig.clear()
        except Exception as e:
            logger.exception(f'{str(e)}')

            self.current_uds_config = DoIPConfig(
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

    def _init_uds_client(self):
        """初始化DoIP客户端和线程"""
        # 创建线程和客户端实例
        self.uds_client_thread = QThread()
        self.uds_client = QUDSClient()

        # 将客户端移到子线程，避免阻塞主线程
        self.uds_client.moveToThread(self.uds_client_thread)

        # 启动线程
        self.uds_client_thread.start()
        logger.info("DoIP客户端线程已启动")

    def _init_external_scripts_thread(self):
        """创建外部脚本执行线程线程"""
        self.external_scripts_thread = QThread()
        self.external_scripts_executor = QExternalScriptsExecutor(self.uds_client)

        self.external_scripts_executor.moveToThread(self.external_scripts_thread)

        # 启动线程
        self.external_scripts_thread.start()
        self.external_scripts_executor.write_signal.connect(self.on_scripts_write)
        logger.info("外部脚本执行线程线程已启动")

    def _init_flash_thread(self):
        """创建flash线程线程"""
        self.flash_thread = QThread()
        self.flash_executor = QFlashExecutor(self.uds_client, self.flash_config, self.flash_file_paths)

        self.flash_executor.moveToThread(self.flash_thread)

        # 启动线程
        self.flash_thread.start()
        self.flash_executor.write_signal.connect(self.on_flash_write)
        self.flash_executor.flash_progress.connect(self.on_set_flash_progress_value)
        self.flash_executor.flash_range.connect(self.on_set_flash_progress_range)
        self.update_flash_variables()

        logger.info("Flash程线程已启动")

    def update_flash_variables(self):
        gFlashVars.files_vars.clear()

        for f in self.flash_config.files:
            if f.name:
                gFlashVars.files_vars[f.name] = FlashFileVars()

    def on_scripts_write(self, script_name: str, message: str):
        html_content = (
            f'<span style="color: #000000;">'
            f'<b>[{script_name}]</b> {message}'
            f'</span>'
        )
        self.plainTextEdit_DataDisplay.appendHtml(html_content)

    def on_flash_write(self, script_name: str, message: str):
        html_content = (
            f'<span style="color: #000000;">'
            f'<b>[{script_name}]</b> {message}'
            f'</span>'
        )
        self.plainTextEdit_DataDisplay.appendHtml(html_content)



    def _init_ui(self):
        """初始化界面组件属性"""
        self.plainTextEdit_DataDisplay.setReadOnly(True)

        icon_disconnected = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.pushButton_ConnectDoIP.setIcon(icon_disconnected)

        # 添加表格
        self.tableView_DoIPTrace = self._add_custom_table_view(self.groupBox_DoIPTrace)

        # 添加DoIPTrace表格到诊断自动化流程
        self.tableView_DoIPTrace_Automated_Process = self._add_custom_table_view(self.groupBox_AutomatedDiagTrace)

        # 共用同一数据模型，需要取消以下两个信号连接
        # self.uds_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # 搜索关键字可以在_connect_uds_client_signals中可以找到
        self.tableView_DoIPTrace_Automated_Process.trace_model = self.tableView_DoIPTrace.trace_model
        self.tableView_DoIPTrace_Automated_Process.setModel(self.tableView_DoIPTrace.trace_model)

        self.uds_services.update_from_json(self.db_manager.get_services_json(self.current_uds_config.config_name))
        # 添加TreeView控件
        self.treeView_DoIPTraceService = self._add_custom_tree_view(self.scrollArea_DiagTree)
        self.treeView_DoIPTraceService.setDragEnabled(True)  # 允许拖拽
        self.treeView_DoIPTraceService.setDragDropMode(QAbstractItemView.DragOnly)  # 仅作为拖拽源
        self.treeView_DoIPTraceService.setDefaultDropAction(Qt.CopyAction)
        # self.treeView_Diag_Process = self._add_custom_tree_view(self.scrollArea_DiagTreeForProcess)
        # self.treeView_Diag_Process.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        # self.treeView_Diag_Process.setModel(self.treeView_DoIPTraceService.model())
        # self.treeView_Diag_Process.expandAll()
        # self.treeView_Diag_Process.setDragEnabled(True)  # 允许拖拽
        # self.treeView_Diag_Process.setDragDropMode(QAbstractItemView.DragOnly)  # 仅作为拖拽源
        # self.treeView_Diag_Process.setDefaultDropAction(Qt.CopyAction)

        self.diag_process_table_view = self._add_diag_process_table_view(self.groupBox_AutomatedDiagProcessTable)

        self.treeView_uds_case = self._add_uds_case_tree_view(self.scrollArea_UdsCaseTree)

        doip_config_names = self.db_manager.get_all_config_names()
        if self.current_uds_config.config_name in doip_config_names:
            for config in doip_config_names:
                self.comboBox_ChooseConfig.addItem(config)
            self.comboBox_ChooseConfig.setCurrentText(self.current_uds_config.config_name)

        self.treeView_uds_case.clicked_case_id.connect(self.diag_process_table_view.model.get_case_step_from_db)

        # 创建Dock view菜单
        dock_diag_tree_action = self.dockWidget_DiagTree.toggleViewAction()
        dock_diag_tree_action.setText("UDS服务")
        self.menu_view.addAction(dock_diag_tree_action)

        dock_write_action = self.dockWidget_write.toggleViewAction()
        dock_write_action.setText("Write窗口")
        self.menu_view.addAction(dock_write_action)

        dock_uds_case_tree_action = self.dockWidget_UdsCaseTree.toggleViewAction()
        dock_uds_case_tree_action.setText("UDS测试Case")
        self.menu_view.addAction(dock_uds_case_tree_action)

        self.menu_view.addSeparator()

        reset_action = QAction("重置视图", self)
        reset_action.triggered.connect(self.on_reset_layout)
        self.menu_view.addAction(reset_action)

        self.resizeDocks([self.dockWidget_DiagTree, self.dockWidget_UdsCaseTree], [200, 200], Qt.Orientation.Horizontal)
        self.resizeDocks([self.dockWidget_write], [150], Qt.Orientation.Vertical)

        self.default_state = self.saveState()

        self.setup_flash_control()

    def on_reset_layout(self):
        self.restoreState(self.default_state)

    def setup_flash_control(self):
        layout = self.scrollArea_FlashFiles.layout()
        if not layout:
            layout = QVBoxLayout(self.scrollArea_FlashFiles)
            layout.setSpacing(15)  # 控件之间的间距

        # 这是一个标准的清空 Layout 的方法
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            # 移除之前的弹簧 (Spacer)
            elif item.spacerItem():
                pass
        # 4. 【循环添加新控件】
        for file_cfg in self.flash_config.files:
            # 使用上面定义的包装类
            self.flash_choose_file_controls.clear()
            self.flash_file_paths.clear()
            self.flash_choose_file_controls[file_cfg.name] = FlashChooseFileControl(self)
            self.flash_choose_file_controls[file_cfg.name].label_FlashFileName.setText(file_cfg.name)
            self.flash_choose_file_controls[file_cfg.name].toolButton_LoadFlashFile.clicked.connect(
                lambda checked=False, name=file_cfg.name, le=self.flash_choose_file_controls[file_cfg.name].lineEdit_FlashFilePath: self.choose_flash_file(name, le)
            )
            layout.addWidget(self.flash_choose_file_controls[file_cfg.name])

        # 5. 【添加弹簧】 (Vertical Spacer)
        # 作用：当控件很少时，把它们顶到最上面，而不是分散在整个区域
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(vertical_spacer)

        # 强制刷新一下 UI
        self.scrollArea_FlashFiles.update()

    @Slot()
    def _save_services_to_db(self):
        self.db_manager.add_services_config(self.current_uds_config.config_name, self.uds_services.to_json())

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
        table_view_uds_trace = DoIPTraceTableView(parent=parent_widget)
        logger.debug(f"父控件：{parent_widget.objectName()}")


        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(table_view_uds_trace)
        layout.setStretchFactor(table_view_uds_trace, 1)

        # 设置父控件尺寸策略（确保父控件也铺满上层）
        parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return table_view_uds_trace

    def _init_signals(self):
        """初始化所有信号槽连接（统一管理）"""
        # UI组件信号
        self._connect_ui_signals()

        # DoIP客户端信号
        self._connect_uds_client_signals()

    def _connect_ui_signals(self):
        """连接UI组件的信号到槽函数"""
        # 按钮信号
        self.pushButton_ConnectDoIP.clicked.connect(self.change_uds_connect_state)
        self.pushButton_SendDoIP.clicked.connect(self._get_input_hex_and_send_raw_uds_payload)
        self.pushButton_EditConfig.clicked.connect(self.open_edit_config_panel)
        self.pushButton_CreateConfig.clicked.connect(self.open_create_config_panel)
        self.pushButton_RefreshIP.clicked.connect(self.get_ip_list)
        self.pushButton_StartFlash.clicked.connect(self.flash_executor.start_flash)
        self.pushButton_StopFlash.clicked.connect(self.flash_executor.stop_flash)

        self.toolButton_LoadExternalScript.clicked.connect(self.choose_external_script)
        # self.toolButton_LoadExternalScript.clicked.connect(self.external_scripts_executor.load_external_script)
        self.pushButton_ExternalScriptRun.clicked.connect(self.external_scripts_executor.run_external_script)
        self.pushButton_ExternalScriptStop.clicked.connect(self.external_scripts_executor.stop_external_script)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.checkBox_TesterPresent.stateChanged.connect(self.uds_client.set_tester_present_timer)
        self.comboBox_TesterIP.currentIndexChanged.connect(self.set_tester_ip)
        self.comboBox_ChooseConfig.currentIndexChanged.connect(self._on_uds_config_chaneged)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_uds_signal.connect(self.uds_client.change_uds_connect_state)
        self.uds_send_raw_payload_signal.connect(self.uds_client.send_payload)

        # treeView双击信号获取触发send_raw_uds_payload_by_diag_tree发送数据
        self.treeView_DoIPTraceService.clicked_node_data.connect(self.send_raw_uds_payload_by_diag_tree)

        self.action_database.triggered.connect(self.open_sql_ui)

        self.treeView_DoIPTraceService.status_bar_message.connect(self.status_bar_show_message)
        self.treeView_DoIPTraceService.data_change_signal.connect(self._save_services_to_db)
        self.treeView_DoIPTraceService.status_bar_message.connect(self.status_bar_show_message)

        self.pushButton_FlashConfig.clicked.connect(self.open_flash_config_panel)

    def choose_flash_file(self, file_name, line_edit):
        abs_path, _ = QFileDialog.getOpenFileName(
            self,  # 父窗口
            "选择刷写文件",  # 标题
            "",  # 默认打开路径 (空字符串表示当前目录)
            "Hex (*.hex);;bin (*.bin);;All Files (*)"  # 文件过滤器，例如 "DLL Files (*.dll);;All Files (*)"
        )
        if abs_path:
            try:
                # 2. 计算相对路径
                # os.getcwd() 获取当前程序运行的工作目录
                # os.path.relpath(目标路径, 基准路径) 计算相对路径
                rel_path = os.path.relpath(abs_path, os.getcwd())
                file_path = rel_path

            except ValueError:
                # Windows 特例：如果文件和程序在不同的盘符（例如 C: 和 D:），
                # 无法计算相对路径，此时会报错，我们保留绝对路径作为后备方案。
                file_path = abs_path
            line_edit.setText(file_path)
            self.flash_file_paths[file_name] = file_path

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
            self.external_scripts_executor.external_script_path = self.external_script_path
            self.external_scripts_executor.load_external_script()

    def _connect_uds_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_client.info_signal.connect(self._on_info_received)
        self.uds_client.warning_signal.connect(self._on_warning_received)
        self.uds_client.error_signal.connect(self._on_error_received)

        self.uds_client.doip_connect_state.connect(self._update_uds_connect_state)

        self.uds_client.doip_response.connect(self.tableView_DoIPTrace.add_trace_data)
        self.uds_client.doip_request.connect(self.tableView_DoIPTrace.add_trace_data)

        # self.uds_client.doip_response.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)
        # self.uds_client.doip_request.connect(self.tableView_DoIPTrace_Automated_Process.add_trace_data)

        self.uds_client.uds_response_finished.connect(self.uds_response_finished)

    @Slot(str)
    def _on_info_received(self, msg):
        self.handle_log_message("INFO", msg)

    @Slot(str)
    def _on_warning_received(self, msg):
        self.handle_log_message("WARNING", msg)

    @Slot(str)
    def _on_error_received(self, msg):
        self.handle_log_message("ERROR", msg)


    def handle_log_message(self, level, message):
        """
        统一日志处理：无时间戳，仅显示 [等级] 和 消息
        """
        # 1. 定义颜色
        colors = {
            "INFO": "#000000",  # 黑色
            "WARNING": "#d35400",  # 焦糖色/深橙色
            "ERROR": "#c0392b"  # 深红色
        }
        color = colors.get(level, "#000000")

        # 2. 构造 HTML (去掉了时间部分)
        # 格式示例: [INFO] 正在连接服务器...
        html_content = (
            f'<span style="color: {color};">'
            f'<b>[{level}]</b> {message}'
            f'</span>'
        )
        self.plainTextEdit_DataDisplay.appendHtml(html_content)


    @Slot()
    def uds_response_finished(self):
        self.pushButton_SendDoIP.setDisabled(False)

    @Slot(int)
    def _on_uds_config_chaneged(self, index: int):
        if index == -1:
            return
        config_name = self.comboBox_ChooseConfig.currentText()
        self.current_uds_config = self.db_manager.query_doip_config(config_name)
        self.db_manager.set_active_config(config_name)
        self.db_manager.init_services_database()

        self.uds_services.update_from_json(self.db_manager.get_services_json(self.current_uds_config.config_name))
        self.treeView_DoIPTraceService.load_uds_service_to_tree_nodes()
        self.treeView_uds_case.refresh()
        self.diag_process_table_view.clear()
        self.update_flash_config()

    def update_flash_config(self):
        self.flash_config = self.db_manager.load_flash_config(self.current_uds_config.config_name)
        self.update_flash_variables()
        self.setup_flash_control()
        self.flash_executor.flash_config = self.flash_config
        self.flash_executor.flash_file_paths = self.flash_file_paths

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
    def _get_input_hex_and_send_raw_uds_payload(self):
        hex_str = self.lineEdit_DoIPRawDate.text().strip()
        if not hex_str:
            logger.warning("发送数据为空，取消发送")
            return
        try:
            byte_data = bytes.fromhex(hex_str)
            self.send_raw_uds_payload(byte_data)
        except ValueError as e:
            logger.error(f"十六进制数据格式错误：{str(e)}，输入内容：{hex_str}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{str(e)}")

    @Slot(bytes)
    def send_raw_uds_payload_by_diag_tree(self, byte_data: bytes):
        if not byte_data:
            logger.warning("发送数据为空，取消发送")
            return

        try:
            if byte_data[0] == 0x27 and byte_data[1] % 2 == 0 and self.uds_client.security_key:
                byte_data = byte_data + self.uds_client.security_key
            self.send_raw_uds_payload(byte_data)
            logger.debug(f"已发送DoIP数据到传输层：{byte_data.hex()}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{str(e)}")

    def send_raw_uds_payload(self, byte_data: bytes):
        """获通过信号与槽的机制传递给DoIP Client并发送出去"""
        if not byte_data:
            logger.warning("发送数据为空，取消发送")
            return

        try:
            self.uds_send_raw_payload_signal.emit(byte_data)
            self.pushButton_SendDoIP.setDisabled(True)
            logger.debug(f"已发送DoIP数据到传输层：{byte_data.hex()}")
        except Exception as e:
            logger.exception(f"发送DoIP数据失败：{str(e)}")

    def change_uds_connect_state(self):
        """切换DoIP连接状态（连接/断开）"""
        # 更新客户端配置
        self._update_uds_client_config()

        # 禁用按钮防止重复点击
        self.pushButton_ConnectDoIP.setDisabled(True)
        self.connect_or_disconnect_uds_signal.emit()
        logger.debug("已触发DoIP连接状态切换信号")

    def _update_uds_client_config(self) -> None:
        """批量更新DoIP客户端配置"""
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，跳过配置更新")
            return

        client = self.uds_client
        client.ecu_ip_address = self.current_uds_config.dut_ipv4_address
        client.ecu_logical_address = self.current_uds_config.dut_logical_address
        client.tcp_port = self.current_uds_config.tcp_port
        client.udp_port = self.current_uds_config.udp_port
        client.activation_type = self.current_uds_config.activation_type
        client.protocol_version = self.current_uds_config.protocol_version
        client.client_logical_address = self.current_uds_config.tester_logical_address
        client.client_ip_address = self.tester_ip_address
        client.use_secure = self.current_uds_config.use_secure
        client.auto_reconnect_tcp = self.auto_reconnect_tcp
        client.vm_specific = self.current_uds_config.oem_specific
        client.GenerateKeyExOptPath = self.current_uds_config.GenerateKeyExOptPath
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
        config_panel = DoIPConfigPanel(parent=self, is_create_new_config=True, configs_name=self.db_manager.get_all_config_names())
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
            self.current_uds_config.GenerateKeyExOptPath = config_panel.config.GenerateKeyExOptPath
            logger.info(
                f"新DoIP配置 - 测试机逻辑地址: 0x{config_panel.config.tester_logical_address:X}, "
                f"ECU逻辑地址: 0x{config_panel.config.dut_logical_address:X}, ECU IP: {config_panel.config.dut_ipv4_address}"
            )
            self.db_manager.add_doip_config(new_config)
            self.comboBox_ChooseConfig.addItem(new_config.config_name)

    @Slot()
    def open_flash_config_panel(self):
        """打开刷写配置面板"""
        flash_panel = FlashConfigPanel(parent=self, flash_config=self.flash_config)
        if flash_panel.exec() == QDialog.Accepted:
            self.flash_config = flash_panel.config
            self.db_manager.save_flash_config(self.current_uds_config.config_name, self.flash_config)
            self.setup_flash_control()
            self.flash_executor.flash_config = self.flash_config


    @Slot()
    def open_edit_config_panel(self):
        """打开DoIP配置编辑面板"""
        config_panel = DoIPConfigPanel(parent=self, configs_name=self.db_manager.get_all_config_names())
        config_panel.setWindowTitle('修改配置')
        config_panel.lineEdit_ConfigName.setText(self.db_manager.get_active_config_name())
        # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
        config_panel.lineEdit_DUT_IP.setText(self.current_uds_config.dut_ipv4_address)
        config_panel.lineEdit_TesterLogicalAddress.setText(f"{self.current_uds_config.tester_logical_address:X}")
        config_panel.lineEdit_DUTLogicalAddress.setText(f"{self.current_uds_config.dut_logical_address:X}")
        config_panel.lineEdit_OEMSpecific.setText(str(self.current_uds_config.oem_specific))
        config_panel.lineEdit_GenerateKeyExOptPath.setText(str(self.current_uds_config.GenerateKeyExOptPath))
        if self.current_uds_config.is_routing_activation_use:
            config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Checked)
        else:
            config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Unchecked)

        if config_panel.exec() == QDialog.Accepted:
            if config_panel.config is None and config_panel.is_delete_config:  # 删除配置
                self.db_manager.delete_doip_config(self.current_uds_config.config_name)
                if config_panel.is_delete_data:
                    self.db_manager.delete_services_config(self.current_uds_config.config_name)
                    self.db_manager.delete_steps_by_case_ids(self.db_manager.get_current_config_uds_cases())
                    self.db_manager.delete_config_uds_cases(self.current_uds_config.config_name)
                doip_config_names = self.db_manager.get_all_config_names()
                if len(doip_config_names) > 0:
                    try:
                        self.comboBox_ChooseConfig.blockSignals(True)
                        self.comboBox_ChooseConfig.clear()
                        self.db_manager.set_active_config(doip_config_names[0])
                        for config in doip_config_names:
                            self.comboBox_ChooseConfig.addItem(config)
                        current_index = self.comboBox_ChooseConfig.currentIndex()
                        self._on_uds_config_chaneged(current_index)
                        self.comboBox_ChooseConfig.blockSignals(False)
                    except Exception as e:
                        self.db_manager.set_active_config('')
                        logger.exception(str(e))
                else:
                    self.comboBox_ChooseConfig.clear()
            elif isinstance(config_panel.config, DoIPConfig):
                self.current_uds_config.config_name = config_panel.config.config_name
                self.current_uds_config.tester_logical_address = config_panel.config.tester_logical_address
                self.current_uds_config.dut_logical_address = config_panel.config.dut_logical_address
                self.current_uds_config.dut_ipv4_address = config_panel.config.dut_ipv4_address
                self.current_uds_config.is_routing_activation_use = config_panel.config.is_routing_activation_use
                self.current_uds_config.oem_specific = config_panel.config.oem_specific
                self.current_uds_config.GenerateKeyExOptPath = config_panel.config.GenerateKeyExOptPath
                self.db_manager.update_doip_config(self.current_uds_config)
                logger.info(
                    f"DoIP配置已更新 - 测试机逻辑地址: 0x{config_panel.config.tester_logical_address:X}, "
                    f"ECU逻辑地址: 0x{config_panel.config.dut_logical_address:X}, ECU IP: {config_panel.config.dut_ipv4_address}"
                )

    @Slot(bool)
    def _update_uds_connect_state(self, state: bool):
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

    @Slot(int)
    def on_set_flash_progress_range(self, progress_range: int):
        self.progressBar_Flash.setRange(0, progress_range)

    @Slot(int)
    def on_set_flash_progress_value(self, progress_val):
        """
        进度条赋值槽函数，接收进度值参数
        :param progress_val: int 进度值，0~100
        """
        # 核心赋值
        self.progressBar_Flash.setValue(progress_val)

        # 可选：进度完成后的回调操作
        if progress_val == 100:
            self.progressBar_Flash.setFormat("刷写完成️")  # 进度条显示文字修改

    def _update_ip_combobox(self):
        """更新IP下拉框"""
        self.comboBox_TesterIP.clear()
        self.comboBox_TesterIP.addItem('Auto')
        for _, ip in self.ip_list[1:]:  # 跳过Auto选项
            self.comboBox_TesterIP.addItem(ip)

    def closeEvent(self, event) -> None:
        """重写关闭事件，优雅退出线程"""
        # 停止Flash线程
        if self.flash_thread:
            self.flash_thread.quit()
            if self.flash_thread.wait(3000):  # 等待3秒超时
                logger.info("Flash线程已正常停止")
            else:
                logger.warning("Flash线程强制退出")

        # 停止外部脚本线程
        if self.external_scripts_thread:
            self.external_scripts_thread.quit()
            if self.external_scripts_thread.wait(3000):  # 等待3秒超时
                logger.info("外部脚本线程已正常停止")
            else:
                logger.warning("外部脚本端线程强制退出")

        # 停止DoIP客户端线程
        if self.uds_client_thread:
            self.uds_client_thread.quit()
            if self.uds_client_thread.wait(3000):  # 等待3秒超时
                logger.info("uds客户端线程已正常停止")
            else:
                logger.warning("uds客户端线程强制退出")

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
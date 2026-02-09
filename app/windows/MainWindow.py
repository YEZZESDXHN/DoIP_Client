import logging
import os
import pprint
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import Signal, QTimer, QThread, Slot, Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMainWindow, QWidget, QAbstractItemView, QVBoxLayout, QSpacerItem, \
    QSizePolicy, QHBoxLayout, QFileDialog, QDialog, QApplication, QToolButton, QFrame
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from app.core.interface_manager import InterfaceManager, CANInterfaceName
from app.core.db_manager import DBManager
from app.core.uds_client import QUDSClient
from app.external_scripts.external_scripts_executor import QExternalScriptsExecutor
from app.flash.flash_executor import QFlashExecutor, FlashFinishType
from app.global_variables import gFlashVars, FlashFileVars
from app.resources.resources import IconEngine
from app.ui.UDSToolMainUI import Ui_UDSToolMainWindow
from app.user_data import UdsService, UdsConfig, UdsOnCANConfig, DoIPConfig
from app.windows.AutomaticDiagnosisProcess_ui import DiagProcessCaseTreeView, DiagProcessTableView
from app.windows.DoIPConfigPanel_ui import DoIPConfigPanel
from app.windows.DoIPTraceTable_ui import DoIPTraceTableView
from app.windows.ExternalScript_Panel import ExternalScriptPanel
from app.windows.FlashConfigPanel import FlashConfig, FlashChooseFileControl, FlashConfigPanel
from app.windows.IG_Panel import CANIGPanel
from app.windows.UdsServicesTreeView_ui import UdsServicesTreeView
from app.windows.custom_status_bar import CustomStatusBar
from app.windows.sql_data_panel import SQLTablePanel

logger = logging.getLogger('UDSTool.' + __name__)


class MainWindow(QMainWindow, Ui_UDSToolMainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    和 Ui_MainWindow（界面元素定义）。
    """
    connect_or_disconnect_uds_signal = Signal()
    uds_send_raw_payload_signal = Signal(bytes)

    def __init__(self):
        super().__init__()
        self.external_script_panel: Optional[ExternalScriptPanel] = None
        self.setupUi(self)
        self.setWindowIcon(IconEngine.get_icon('car_connected'))
        self.setWindowTitle("UDS Client")
        self.interface_channels = None
        self.current_can_interface = None

        self.can_ig_panel = None

        empty_title = QWidget()
        self.dockWidget.setTitleBarWidget(empty_title)

        self.tester_ip_address: Optional[str] = None
        self.current_uds_config: Optional[UdsConfig] = None
        self.db_manager: Optional[DBManager] = None
        self.uds_client: Optional[QUDSClient] = None
        self.uds_client_thread = None
        self.auto_reconnect_tcp = True
        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config
        self.external_script_path: str = ''

        self.db_path = 'Database/database.db'
        self.init_database(self.db_path)
        self.uds_services: Optional[UdsService] = None
        self._init_current_uds_config()
        self.current_uds_config.is_can_uds = False

        self.add_external_lib()

        self.flash_config: Optional[FlashConfig] = self.db_manager.flash_config_db.get_flash_config(
            self.current_uds_config.config_name)
        if not self.flash_config:
            self.flash_config = FlashConfig()
        self.flash_file_paths = {}
        self.flash_choose_file_controls = {}
        self.flash_timer = QTimer()  # 实时计时定时器
        self.flash_timer.setInterval(100)  # 计时精度：100ms，0.1秒刷新一次，足够流畅
        self.flash_timer.timeout.connect(self.update_flash_time)  # 定时刷新时间
        self.flash_start_dt = None

        self._init_uds_client()
        self._init_interface_manager()
        self._init_external_scripts_thread()
        self._init_flash_thread()

        # 初始化UI、客户端、信号、IP列表
        self._init_ui()

        self._init_signals()

    def _init_interface_manager(self):
        self.interface_manager = InterfaceManager()
        self.interface_manager.is_can_interface = self.current_uds_config.is_can_uds
        self.interface_manager_thread = QThread()
        # self.interface_manager = InterfaceManager()

        self.interface_manager.moveToThread(self.interface_manager_thread)
        self.interface_manager.signal_interface_channels.connect(self.on_interface_update)

        # 启动线程
        self.interface_manager_thread.start()
        logger.info("InterfaceManager线程线程已启动")

    def update_can_interface(self):
        channels = []
        can_interface_name = self.comboBox_HardwareType.currentText()
        if can_interface_name in list(CANInterfaceName):
            for ch in self.interface_channels:
                channels.append(self.interface_manager.can_interface_manager.get_display_text(ch, can_interface_name))
            # if can_interface_name == CANInterfaceName.vector:
            #     for ch in self.interface_channels:
            #         channels.append(
            #             f"{ch['interface']} - {ch['vector_channel_config'].name} - channel {ch['channel']}  {ch['serial']}")
            #
            # else:
            #     if can_interface_name == CANInterfaceName.tosun:
            #         for ch in self.interface_channels:
            #             channels.append(
            #                 f"{ch['interface']} - {ch['name']} - channel {ch['channel']}  {ch['sn']}")
        self.comboBox_HardwareChannel.addItems(channels)

    def on_interface_update(self, interface_channels):
        try:
            self.comboBox_HardwareChannel.clear()
            self.interface_channels = interface_channels
            if self.current_uds_config.is_can_uds:
                self.update_can_interface()
            else:

                ips = []
                for _, ip in self.interface_channels:
                    ips.append(ip)
                self.comboBox_HardwareChannel.addItems(ips)
            if self.interface_channels:
                self.current_can_interface = self.interface_channels[0]
        except Exception as e:
            logger.exception(f'更新channel失败，{e}')

    def add_external_lib(self):
        # ExternalLib sys.path
        lib_dir = os.path.dirname(os.path.abspath('ExternalLib'))
        if lib_dir not in sys.path:
            sys.path.append(lib_dir)

    def _init_current_uds_config(self):
        try:
            current_config_name = self.db_manager.current_uds_config_db.get_active_config_name()
            self.current_uds_config = self.db_manager.uds_config_db.get_uds_config(current_config_name)
            if not self.current_uds_config:
                uds_config_names = self.db_manager.uds_config_db.get_all_config_names()
                if len(uds_config_names) > 0:
                    try:
                        self.comboBox_ChooseConfig.clear()
                        self.db_manager.current_uds_config_db.set_active_config(uds_config_names[0])
                        for config in uds_config_names:
                            self.comboBox_ChooseConfig.addItem(config)
                        self.comboBox_ChooseConfig.setCurrentText(self.current_uds_config.config_name)
                        # self.current_uds_config = self.db_manager.query_uds_config(current_config_name)

                    except Exception as e:
                        self.db_manager.current_uds_config_db.set_active_config('')
                        logger.exception(str(e))
                else:
                    self.comboBox_ChooseConfig.clear()
        except Exception as e:
            logger.exception(f'{str(e)}')

            self.current_uds_config = UdsConfig(
                config_name='DoIP_config_panel_default',
                can=UdsOnCANConfig(),
                doip=DoIPConfig(
                    tester_logical_address=0x7e2,
                    dut_logical_address=0x773,
                    dut_ipv4_address='172.16.104.70'
                )
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
        self.custom_status_bar.label_SendPrompt.setText(msg)

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
        self.external_scripts_executor = QExternalScriptsExecutor(uds_client=self.uds_client,
                                                                  db_manager=self.db_manager,
                                                                  config_name=self.current_uds_config.config_name)

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
        self.checkBox_FlashMessageDisplay.stateChanged.connect(self.on_display_trace_change)
        self.flash_executor.flash_finish.connect(self.on_flash_finish)
        self.update_flash_variables()

        logger.info("Flash程线程已启动")

    def update_flash_variables(self):
        gFlashVars.udsoncan_files_vars.clear()
        gFlashVars.udsonip_files_vars.clear()
        if not self.flash_config:
            return
        for f in self.flash_config.udsonip_config.files:
            if f.name:
                gFlashVars.udsonip_files_vars[f.name] = FlashFileVars()
        for f in self.flash_config.udsoncan_config.files:
            if f.name:
                gFlashVars.udsoncan_files_vars[f.name] = FlashFileVars()

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

    def _init_ui_icon(self):
        self.pushButton_ConnectDoIP.setIcon(IconEngine.get_icon("unlink", 'red'))
        self.pushButton_SendDoIP.setIcon(IconEngine.get_icon("send", 'blue'))
        self.pushButton_CreateConfig.setIcon(IconEngine.get_icon("circles_add"))
        self.pushButton_EditConfig.setIcon(IconEngine.get_icon("pencil"))
        self.pushButton_RefreshIP.setIcon(IconEngine.get_icon("refresh"))
        # self.checkBox_AotuReconnect.setIcon(IconEngine.get_icon("auto_start"))
        self.pushButton_StartFlash.setIcon(IconEngine.get_icon("start", 'blue'))
        self.pushButton_StopFlash.setIcon(IconEngine.get_icon("stop", 'red'))
        self.pushButton_FlashConfig.setIcon(IconEngine.get_icon("config"))

    def _add_app_start_button_to_menu(self):
        self.btn_widget = QWidget()
        layout = QHBoxLayout(self.btn_widget)
        layout.setContentsMargins(5, 0, 10, 0)
        layout.setSpacing(5)

        self.start_btn = QToolButton()
        # self.start_btn.setText("⚡")
        self.start_btn.setIcon(IconEngine.get_icon("flashlight", '#FFB900'))
        self.start_btn.setFixedSize(28, 24)
        self.start_btn.setStyleSheet("color: #FFD700; border: none; font-size: 16px; font-weight: bold;")
        self.start_btn.clicked.connect(self.on_start_clicked)

        # 3. 创建停止按钮 (Stop)
        self.stop_btn = QToolButton()
        # self.stop_btn.setText("⬢")
        self.stop_btn.setIcon(IconEngine.get_icon("circle", 'red'))
        self.stop_btn.setFixedSize(28, 24)
        self.stop_btn.setEnabled(False)  # 初始禁用
        self.stop_btn.setStyleSheet("color: #808080; border: none; font-size: 16px;")
        self.stop_btn.clicked.connect(self.on_stop_clicked)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)  # 设置为垂直线
        separator.setFrameShadow(QFrame.Plain)  # 设置为平实风格，避免多余阴影
        separator.setFixedWidth(1)  # 线条宽度设为 1 像素
        separator.setFixedHeight(16)  # 线条高度（根据你的菜单栏高度调整，通常 16-20 较好）
        separator.setStyleSheet("background-color: #D0D0D0; border: none;")  # 设置线条颜色

        layout.addSpacing(5)  # 分隔符前的留白
        layout.addWidget(separator)
        layout.addSpacing(5)  # 分隔符后的留白，确保离 File 菜单有间距

        # 4. 关键：注入到你 Designer 生成的 menuBar 左侧
        # 注意：self.menuBar 是从 QMainWindow 继承的方法，会自动获取 Designer 里的那个菜单栏
        self.menuBar().setCornerWidget(self.btn_widget, Qt.TopLeftCorner)

    def on_start_clicked(self):
        print("工程启动")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        # self.stop_btn.setStyleSheet("color: red; border: none; font-size: 16px;")

    def on_stop_clicked(self):
        print("工程停止")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        # self.stop_btn.setStyleSheet("color: #808080; border: none; font-size: 16px;")

    def _init_ui(self):
        """初始化界面组件属性"""
        self._add_app_start_button_to_menu()

        self.plainTextEdit_DataDisplay.setReadOnly(True)

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

        self.uds_services = self.db_manager.service_config_db.get_service_config(self.current_uds_config.config_name)
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

        uds_config_names = self.db_manager.uds_config_db.get_all_config_names()
        if self.current_uds_config.config_name in uds_config_names:
            for config in uds_config_names:
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

        self.tabifyDockWidget(self.dockWidget_DiagTree, self.dockWidget_UdsCaseTree)
        self.dockWidget_DiagTree.raise_()
        self.dockWidget_DiagTree.show()
        self.default_state = self.saveState()

        self.setup_flash_control()

        self._init_ui_icon()

        self._init_status_bar()

        self.comboBox_HardwareType.addItem('Windows Ethernet')
        self.comboBox_HardwareType.addItems(self.interface_manager.can_interface_manager.adapters.keys())

        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        # 将主题 Action 加入组
        self.theme_group.addAction(self.action_Fusion)
        self.theme_group.addAction(self.action_Default)

        self.setup_ig_panel()
        self.setup_external_script_panel()

    def set_theme_to_default(self):
        app = QApplication.instance()
        app.setStyle("WindowsVista")

    def set_theme_to_fusion(self):
        app = QApplication.instance()
        app.setStyle("Fusion")

    def on_hardware_type_change(self, index: int):
        current_text = self.comboBox_HardwareType.currentText()
        if current_text in list(CANInterfaceName):
            self.current_uds_config.is_can_uds = True
            self.interface_manager.is_can_interface = True
            self.interface_manager.can_interface_name = current_text

            # self.interface_channels

        else:
            self.current_uds_config.is_can_uds = False
            self.interface_manager.is_can_interface = False
        self.pushButton_RefreshIP.clicked.emit()

    def _init_status_bar(self):
        self.custom_status_bar = CustomStatusBar(self)
        self.status_bar.addWidget(self.custom_status_bar, 1)

        self.custom_status_bar.pushButton_ConnectState.setIcon(IconEngine.get_icon("unlink", 'red'))

    def on_reset_layout(self):
        self.restoreState(self.default_state)

    def setup_ig_panel(self):
        layout = self.tab_CANIG.layout()
        if not layout:
            layout = QVBoxLayout(self.tab_CANIG)
            layout.setSpacing(15)  # 控件之间的间距

        self.can_ig_panel = CANIGPanel(interface_manager=self.interface_manager, db_manager=self.db_manager,
                                       config=self.current_uds_config.config_name, parent=self)
        layout.addWidget(self.can_ig_panel)

    def setup_external_script_panel(self):
        layout = self.tab_ExternalScript.layout()
        if not layout:
            layout = QVBoxLayout(self.tab_ExternalScript)
            layout.setSpacing(15)  # 控件之间的间距

        self.external_script_panel = ExternalScriptPanel(db_manager=self.db_manager,
                                                         config_name=self.current_uds_config.config_name, parent=self)
        layout.addWidget(self.external_script_panel)

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
        if not self.flash_config:
            return

        self.flash_choose_file_controls.clear()
        self.flash_file_paths.clear()
        if self.current_uds_config.is_can_uds:
            config = self.flash_config.udsoncan_config
        else:
            config = self.flash_config.udsonip_config
        for file_cfg in config.files:
            # 使用上面定义的包装类
            self.flash_choose_file_controls[file_cfg.name] = FlashChooseFileControl(self)
            if file_cfg.default_path:
                self.flash_choose_file_controls[file_cfg.name].lineEdit_FlashFilePath.setText(file_cfg.default_path)
                self.flash_file_paths[file_cfg.name] = file_cfg.default_path
            self.flash_choose_file_controls[file_cfg.name].label_FlashFileName.setText(file_cfg.name)
            # self.flash_choose_file_controls[file_cfg.name].toolButton_LoadFlashFile.clicked.connect(
            #     lambda checked=False, name=file_cfg.name, le=self.flash_choose_file_controls[file_cfg.name].lineEdit_FlashFilePath: self.choose_flash_file(name, le)
            # )
            self.flash_choose_file_controls[file_cfg.name].toolButton_LoadFlashFile.clicked.connect(
                lambda checked=False, name=file_cfg.name,
                       le=self.flash_choose_file_controls[file_cfg.name].lineEdit_FlashFilePath: self.choose_flash_file(
                    name, le)
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
        self.db_manager.service_config_db.save_service_config(self.current_uds_config.config_name, self.uds_services)

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
        self.pushButton_RefreshIP.clicked.connect(self.interface_manager.scan_interfaces)

        # self.pushButton_RefreshIP.clicked.emit()
        self.pushButton_StartFlash.clicked.connect(self.flash_executor.start_flash)
        self.pushButton_StartFlash.clicked.connect(self.on_start_flash)

        self.pushButton_StopFlash.clicked.connect(self.stop_flash)
        self.pushButton_ClearDoIPTrace.clicked.connect(self.tableView_DoIPTrace._clear_data)

        # self.toolButton_LoadExternalScript.clicked.connect(self.choose_external_script)
        # # self.toolButton_LoadExternalScript.clicked.connect(self.external_scripts_executor.load_external_script)
        # self.pushButton_ExternalScriptRun.clicked.connect(self.external_scripts_executor.run_external_script)
        # self.pushButton_ExternalScriptStop.clicked.connect(self.external_scripts_executor.stop_external_script)
        self.external_script_panel.pushButton_start.clicked.connect(self.external_scripts_executor.run_external_scripts)
        self.external_script_panel.pushButton_stop.clicked.connect(
            self.stop_run_external_scripts)
        self.external_scripts_executor.scripts_run_start.connect(self.external_script_panel.on_run_script)
        self.external_scripts_executor.scripts_run_finish_state.connect(self.external_script_panel.on_run_finish)
        self.external_scripts_executor.scripts_run_state.connect(self.external_script_panel.update_scripts_run_state)
        self.external_scripts_executor.script_run_state.connect(self.external_script_panel.update_script_run_state)

        # 复选框和下拉框信号
        self.checkBox_AotuReconnect.stateChanged.connect(self.set_auto_reconnect_tcp)
        self.checkBox_TesterPresent.stateChanged.connect(self.uds_client.set_tester_present_timer)
        self.comboBox_HardwareChannel.currentIndexChanged.connect(self.set_interface_channel)
        self.comboBox_HardwareType.currentIndexChanged.connect(self.on_hardware_type_change)
        self.comboBox_HardwareType.currentIndexChanged.emit(-1)
        self.comboBox_HardwareType.currentIndexChanged.connect(self.setup_flash_control)
        self.comboBox_ChooseConfig.currentIndexChanged.connect(self._on_uds_config_chaneged)

        # 自定义信号（传递给DoIP客户端）
        self.connect_or_disconnect_uds_signal.connect(self.uds_client.change_uds_connect_state)
        self.uds_send_raw_payload_signal.connect(self.uds_client.send_payload)

        # treeView双击信号获取触发send_raw_uds_payload_by_diag_tree发送数据
        self.treeView_DoIPTraceService.clicked_node_data.connect(self.send_raw_uds_payload_by_diag_tree)

        self.action_database.triggered.connect(self.open_sql_ui)

        self.action_Default.triggered.connect(self.set_theme_to_default)
        self.action_Fusion.triggered.connect(self.set_theme_to_fusion)

        self.treeView_DoIPTraceService.status_bar_message.connect(self.status_bar_show_message)
        self.treeView_DoIPTraceService.data_change_signal.connect(self._save_services_to_db)

        self.pushButton_FlashConfig.clicked.connect(self.open_flash_config_panel)

    def stop_run_external_scripts(self):
        self.external_scripts_executor.stop_run_external_scripts()

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

    # def choose_external_script(self):
    #     abs_path, _ = QFileDialog.getOpenFileName(
    #         self,  # 父窗口
    #         "选择外部Python脚本",  # 标题
    #         "",  # 默认打开路径 (空字符串表示当前目录)
    #         "Python Files (*.py)"  # 文件过滤器，例如 "DLL Files (*.dll);;All Files (*)"
    #     )
    #
    #     if abs_path:
    #         try:
    #             # 2. 计算相对路径
    #             # os.getcwd() 获取当前程序运行的工作目录
    #             # os.path.relpath(目标路径, 基准路径) 计算相对路径
    #             rel_path = os.path.relpath(abs_path, os.getcwd())
    #
    #             # 3. 将相对路径填入输入框
    #             self.external_script_path = rel_path
    #
    #
    #         except ValueError:
    #             # Windows 特例：如果文件和程序在不同的盘符（例如 C: 和 D:），
    #             # 无法计算相对路径，此时会报错，我们保留绝对路径作为后备方案。
    #             self.external_script_path = abs_path
    #         self.lineEdit_ExternalScriptPath.setText(self.external_script_path)
    #         self.external_scripts_executor.external_script_path = self.external_script_path
    #         self.external_scripts_executor.load_external_script()

    def _connect_uds_client_signals(self):
        """连接DoIP客户端的信号到槽函数"""
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，无法连接信号")
            return

        self.uds_client.info_signal.connect(self._on_info_received)
        self.uds_client.warning_signal.connect(self._on_warning_received)
        self.uds_client.error_signal.connect(self._on_error_received)

        self.uds_client.uds_connect_state.connect(self._update_uds_connect_state)

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
        self.current_uds_config = self.db_manager.uds_config_db.get_uds_config(config_name)
        self.db_manager.current_uds_config_db.set_active_config(config_name)
        # self.db_manager.init_services_database()
        self.can_ig_panel.set_config(config_name)
        self.external_script_panel.set_config(config_name)

        self.uds_services = self.db_manager.service_config_db.get_service_config(self.current_uds_config.config_name)
        self.treeView_DoIPTraceService.load_uds_service_to_tree_nodes()
        self.treeView_uds_case.refresh()
        self.diag_process_table_view.clear()
        self.update_flash_config()

    def update_flash_config(self):
        self.flash_config = self.db_manager.flash_config_db.get_flash_config(self.current_uds_config.config_name)
        self.update_flash_variables()
        self.setup_flash_control()
        self.flash_executor.flash_config = self.flash_config
        self.flash_executor.flash_file_paths = self.flash_file_paths

    def set_interface_channel(self, index: int):
        """设置测试机IP"""
        if self.current_uds_config.is_can_uds:
            self.current_can_interface = self.interface_channels[index]
        else:
            self.tester_ip_address = self.comboBox_HardwareChannel.currentText()
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

    def _change_ui_state(self, set_disabled: bool):
        self.pushButton_ConnectDoIP.setDisabled(set_disabled)
        self.comboBox_HardwareType.setDisabled(set_disabled)
        self.comboBox_ChooseConfig.setDisabled(set_disabled)
        self.comboBox_HardwareChannel.setDisabled(set_disabled)
        self.pushButton_RefreshIP.setDisabled(set_disabled)
        self.pushButton_EditConfig.setDisabled(set_disabled)
        self.pushButton_CreateConfig.setDisabled(set_disabled)
        self.checkBox_AotuReconnect.setDisabled(set_disabled)

    def change_uds_connect_state(self):
        """切换DoIP连接状态（连接/断开）"""
        self._change_ui_state(True)

        # 更新客户端配置
        self._update_uds_client_config()
        self.connect_or_disconnect_uds_signal.emit()
        logger.debug("已触发DoIP连接状态切换信号")

    def _update_uds_client_config(self) -> None:
        """批量更新DoIP客户端配置"""
        if not self.uds_client:
            logger.warning("DoIP客户端未初始化，跳过配置更新")
            return

        client = self.uds_client
        if client._uds_client or client.cantp_stack:
            return
        client.is_can_uds = self.current_uds_config.is_can_uds
        client.uds_on_ip_config = self.current_uds_config.doip
        client.uds_on_can_config = self.current_uds_config.can

        client.client_ip_address = self.tester_ip_address
        client.auto_reconnect_tcp = self.auto_reconnect_tcp

        client.can_interface = self.current_can_interface

        client.uds_request_timeout = self.uds_request_timeout
        client.uds_config = self.uds_config

        client.load_generate_key_ex_opt(self.current_uds_config.GenerateKeyExOptPath)

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
        """打开新建uds配置面板"""
        config_panel = DoIPConfigPanel(parent=self, is_create_new_config=True,
                                       configs_name=self.db_manager.uds_config_db.get_all_config_names())
        config_panel.setWindowTitle('新建配置')
        new_config = UdsConfig()

        config_panel.config.is_can_uds = self.current_uds_config.is_can_uds
        if self.current_uds_config.is_can_uds:
            config_panel.groupBox_DoIPConfig.setVisible(False)

            # 设置配置面板初始值
            # ********************UDS on CAN config**********************
            if new_config.can.is_fd:
                config_panel.checkBox_IsFD.setCheckState(Qt.CheckState.Checked)
            else:
                config_panel.checkBox_IsFD.setCheckState(Qt.CheckState.Unchecked)
            config_panel.lineEdit_CANReqID.setText(f"{new_config.can.req_id:X}")
            config_panel.lineEdit_CANRespID.setText(f"{new_config.can.resp_id:X}")
            config_panel.lineEdit_CANFunID.setText(f"{new_config.can.fun_id:X}")

            # ********************CAN Bus config**********************
            config_panel.comboBox_CANControllerMode.setCurrentText(new_config.can.controller_mode)
            config_panel.comboBox_CANControllerMode.currentIndexChanged.emit(
                config_panel.comboBox_CANControllerMode.currentIndex())

            config_panel.lineEdit_CANControllerClockFrequency.setText(str(new_config.can.f_clock))
            config_panel.lineEdit_NormalBitrate.setText(str(new_config.can.nom_bitrate))
            config_panel.lineEdit_NormalSamplePoint.setText(str(new_config.can.nom_sample_point))
            config_panel.lineEdit_DataBitrate.setText(str(new_config.can.data_bitrate))
            config_panel.lineEdit_DataSamplePoint.setText(str(new_config.can.data_sample_point))

            # ********************CAN TP config**********************
        else:
            config_panel.groupBox_CANTPConfig.setVisible(False)
            config_panel.groupBox_CANBusConfig.setVisible(False)
            config_panel.groupBox_UDSonCANConfig.setVisible(False)

            # config_panel.lineEdit_ConfigName.setText(self.db_manager.get_active_config_name())
            # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
            config_panel.lineEdit_DUT_IP.setText(new_config.doip.dut_ipv4_address)
            config_panel.lineEdit_TesterLogicalAddress.setText(f"{new_config.doip.tester_logical_address:X}")
            config_panel.lineEdit_DUTLogicalAddress.setText(f"{new_config.doip.dut_logical_address:X}")
            config_panel.lineEdit_OEMSpecific.setText(str(new_config.doip.oem_specific))
            config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Checked)

        if config_panel.exec() == QDialog.Accepted:
            new_config = config_panel.config
            try:
                self.db_manager.uds_config_db.upsert_uds_config(new_config)
            except Exception as e:
                logger.exception(f"保存配置{new_config.config_name}失败，{e}")
            self.comboBox_ChooseConfig.addItem(new_config.config_name)

    @Slot()
    def open_flash_config_panel(self):
        """打开刷写配置面板"""
        flash_panel = FlashConfigPanel(parent=self, flash_config=self.flash_config)
        if flash_panel.exec() == QDialog.Accepted:
            self.flash_config = flash_panel.config
            self.db_manager.flash_config_db.save_flash_config(self.current_uds_config.config_name, self.flash_config)
            self.setup_flash_control()
            self.flash_executor.flash_config = self.flash_config

    @Slot()
    def open_edit_config_panel(self):
        """打开DoIP配置编辑面板"""
        config_panel = DoIPConfigPanel(parent=self, configs_name=self.db_manager.uds_config_db.get_all_config_names())
        config_panel.setWindowTitle('修改配置')

        config_panel.lineEdit_ConfigName.setText(self.current_uds_config.config_name)
        config_panel.config.is_can_uds = self.current_uds_config.is_can_uds
        config_panel.lineEdit_GenerateKeyExOptPath.setText(str(self.current_uds_config.GenerateKeyExOptPath))
        if self.current_uds_config.is_can_uds:
            config_panel.groupBox_DoIPConfig.setVisible(False)

            # ********************UDS on CAN config**********************
            if self.current_uds_config.can.is_fd:
                config_panel.checkBox_IsFD.setCheckState(Qt.CheckState.Checked)
            else:
                config_panel.checkBox_IsFD.setCheckState(Qt.CheckState.Unchecked)
            config_panel.lineEdit_CANReqID.setText(f"{self.current_uds_config.can.req_id:X}")
            config_panel.lineEdit_CANRespID.setText(f"{self.current_uds_config.can.resp_id:X}")
            config_panel.lineEdit_CANFunID.setText(f"{self.current_uds_config.can.fun_id:X}")

            # ********************CAN Bus config**********************
            config_panel.comboBox_CANControllerMode.setCurrentText(self.current_uds_config.can.controller_mode)
            config_panel.comboBox_CANControllerMode.currentIndexChanged.emit(
                config_panel.comboBox_CANControllerMode.currentIndex())

            config_panel.lineEdit_CANControllerClockFrequency.setText(str(self.current_uds_config.can.f_clock))
            config_panel.lineEdit_NormalBitrate.setText(str(self.current_uds_config.can.nom_bitrate))
            config_panel.lineEdit_NormalSamplePoint.setText(str(self.current_uds_config.can.nom_sample_point))
            config_panel.lineEdit_DataBitrate.setText(str(self.current_uds_config.can.data_bitrate))
            config_panel.lineEdit_DataSamplePoint.setText(str(self.current_uds_config.can.data_sample_point))

            # ********************CAN TP config**********************
        else:
            config_panel.groupBox_CANTPConfig.setVisible(False)
            config_panel.groupBox_CANBusConfig.setVisible(False)
            config_panel.groupBox_UDSonCANConfig.setVisible(False)

            # ********************DoIP config**********************
            # 设置配置面板初始值（格式化十六进制，去掉0x前缀）
            config_panel.lineEdit_DUT_IP.setText(self.current_uds_config.doip.dut_ipv4_address)
            config_panel.lineEdit_TesterLogicalAddress.setText(
                f"{self.current_uds_config.doip.tester_logical_address:X}")
            config_panel.lineEdit_DUTLogicalAddress.setText(f"{self.current_uds_config.doip.dut_logical_address:X}")
            config_panel.lineEdit_OEMSpecific.setText(str(self.current_uds_config.doip.oem_specific))
            if self.current_uds_config.doip.is_routing_activation_use:
                config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Checked)
            else:
                config_panel.checkBox_RouteActive.setCheckState(Qt.CheckState.Unchecked)

        if config_panel.exec() == QDialog.Accepted:
            if config_panel.config is None and config_panel.is_delete_config:  # 删除配置
                # self.db_manager.uds_config_db.delete_uds_config(self.current_uds_config.config_name)
                # if config_panel.is_delete_data:
                #     self.db_manager.delete_services_config(self.current_uds_config.config_name)
                #     self.db_manager.delete_steps_by_case_ids(self.db_manager.get_current_config_uds_cases())
                #     self.db_manager.delete_config_uds_cases(self.current_uds_config.config_name)
                #     self.db_manager.delete_can_ig_by_config(self.current_uds_config.config_name)
                self.db_manager.delete_config(self.current_uds_config.config_name)
                doip_config_names = self.db_manager.uds_config_db.get_all_config_names()
                if len(doip_config_names) > 0:
                    try:
                        self.comboBox_ChooseConfig.blockSignals(True)
                        self.comboBox_ChooseConfig.clear()
                        self.db_manager.current_uds_config_db.set_active_config(doip_config_names[0])
                        for config in doip_config_names:
                            self.comboBox_ChooseConfig.addItem(config)
                        current_index = self.comboBox_ChooseConfig.currentIndex()
                        self._on_uds_config_chaneged(current_index)
                        self.comboBox_ChooseConfig.blockSignals(False)
                    except Exception as e:
                        self.db_manager.current_uds_config_db.set_active_config('')
                        logger.exception(str(e))
                else:
                    self.comboBox_ChooseConfig.clear()
            elif isinstance(config_panel.config, UdsConfig):
                self.current_uds_config.config_name = config_panel.config.config_name
                self.current_uds_config.GenerateKeyExOptPath = config_panel.config.GenerateKeyExOptPath
                if self.current_uds_config.is_can_uds:
                    # ********************UDS on CAN config**********************
                    if config_panel.checkBox_IsFD.isChecked():
                        self.current_uds_config.can.is_fd = True
                    else:
                        self.current_uds_config.can.is_fd = False
                    self.current_uds_config.can.req_id = config_panel.config.can.req_id
                    self.current_uds_config.can.resp_id = config_panel.config.can.resp_id
                    self.current_uds_config.can.fun_id = config_panel.config.can.fun_id

                    # ********************CAN bus config**********************
                    self.current_uds_config.can.controller_mode = config_panel.comboBox_CANControllerMode.currentText()

                    self.current_uds_config.can.f_clock = int(config_panel.lineEdit_CANControllerClockFrequency.text())
                    self.current_uds_config.can.nom_bitrate = int(config_panel.lineEdit_NormalBitrate.text())
                    self.current_uds_config.can.nom_sample_point = float(config_panel.lineEdit_NormalSamplePoint.text())
                    self.current_uds_config.can.data_bitrate = int(config_panel.lineEdit_DataBitrate.text())
                    self.current_uds_config.can.data_sample_point = float(config_panel.lineEdit_DataSamplePoint.text())

                    # ********************CAN TP config**********************

                    self.db_manager.uds_config_db.upsert_uds_config(self.current_uds_config)
                else:
                    # ********************DoIP config**********************
                    self.current_uds_config.doip.tester_logical_address = config_panel.config.doip.tester_logical_address
                    self.current_uds_config.doip.dut_logical_address = config_panel.config.doip.dut_logical_address
                    self.current_uds_config.doip.dut_ipv4_address = config_panel.config.doip.dut_ipv4_address
                    self.current_uds_config.doip.is_routing_activation_use = config_panel.config.doip.is_routing_activation_use
                    self.current_uds_config.doip.oem_specific = config_panel.config.doip.oem_specific

                    self.db_manager.uds_config_db.upsert_uds_config(self.current_uds_config)
                    logger.info(
                        f"DoIP配置已更新 - 测试机逻辑地址: 0x{config_panel.config.doip.tester_logical_address:X}, "
                        f"ECU逻辑地址: 0x{config_panel.config.doip.dut_logical_address:X}, ECU IP: {config_panel.config.doip.dut_ipv4_address}"
                    )

    @Slot(bool)
    def _update_uds_connect_state(self, state: bool):
        """更新DoIP连接状态的UI显示"""
        self.pushButton_ConnectDoIP.setDisabled(False)
        if state:
            icon_name = "link"
            self.pushButton_ConnectDoIP.setText("已连接")
            self.pushButton_ConnectDoIP.setIcon(IconEngine.get_icon(icon_name, 'green'))
            self.custom_status_bar.pushButton_ConnectState.setIcon(IconEngine.get_icon(icon_name, 'green'))
            logger.info(f"DoIP连接状态已更新为：已连接")
        else:
            icon_name = "unlink"
            self.pushButton_ConnectDoIP.setText("未连接")
            self.pushButton_ConnectDoIP.setIcon(IconEngine.get_icon(icon_name, 'red'))
            self.custom_status_bar.pushButton_ConnectState.setIcon(IconEngine.get_icon(icon_name, 'red'))
            self._change_ui_state(False)
            logger.info(f"DoIP连接状态已更新为：未已连接")

    @Slot(int)
    def on_set_flash_progress_range(self, progress_range: int):
        self.progressBar_Flash.setRange(0, progress_range)

    @Slot(int)
    def on_set_flash_progress_value(self, progress_val):
        self.progressBar_Flash.setValue(progress_val)

    @Slot(int)
    def on_display_trace_change(self, state):
        self.flash_executor.display_trace = 0 if state == 0 else 1

    def on_flash_finish(self, finish_type: FlashFinishType):
        self.flash_timer.stop()
        duration = (datetime.now() - self.flash_start_dt).total_seconds()
        time_str = f"{int(duration // 60):02d}:{duration % 60:.2f}"
        self.label_FlashState.setText(f"{finish_type.value} | {time_str}")

        if finish_type == FlashFinishType.success:
            self.set_flash_state_label_color("green")
        else:
            self.set_flash_state_label_color("red")

        self.pushButton_StopFlash.setDisabled(True)
        self.pushButton_StartFlash.setDisabled(False)

    @Slot()
    def on_start_flash(self):
        self.flash_start_dt = datetime.now()
        self.flash_timer.start()
        self.set_flash_state_label_color("orange")  # 刷写中-橙色

        self.pushButton_StopFlash.setDisabled(False)
        self.pushButton_StartFlash.setDisabled(True)

    def update_flash_time(self):
        if self.flash_start_dt:
            duration = (datetime.now() - self.flash_start_dt).total_seconds()
            time_str = f"{int(duration // 60):02d}:{duration % 60:.2f}"
            self.label_FlashState.setText(f"【正在刷写】请勿断电 |  {time_str}")

    def set_flash_state_label_color(self, color):
        self.label_FlashState.setStyleSheet(f"QLabel {{ color: {color}; }}")

    @Slot()
    def stop_flash(self):
        self.flash_executor.stop_flash_flag = True

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

        if self.interface_manager_thread:
            self.interface_manager_thread.quit()
            if self.interface_manager_thread.wait(3000):  # 等待3秒超时
                logger.info("interface_manager_thread线程已正常停止")
            else:
                logger.warning("interface_manager_thread线程强制退出")

        event.accept()

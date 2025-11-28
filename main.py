import logging.config
import sys
from typing import Optional

from PySide6.QtCore import QThread, Slot, Signal
from PySide6.QtWidgets import QMainWindow, QApplication
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig
from udsoncan.configs import default_client_config

from DoIPConfigPanel import DoIPConfigPanel
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

    def __init__(self):
        super().__init__()

        # 1. 调用生成的 setupUi 方法
        # 这将初始化所有界面元素（按钮、标签等）
        self.uds_on_ip_client = None
        self.uds_on_ip_client_thread = None
        self.setupUi(self)
        # self.ecu_ip = '127.0.0.1'
        # self.client_ip = '127.0.0.1'
        # self.client_logical_address = 101
        # self.ecu_logical_address = 200
        self.ip_list = []
        self.ecu_ip_address = '172.16.104.70'
        self.client_ip_address = '172.16.104.54'
        self.client_logical_address = 0x7e2
        self.ecu_logical_address = 0x773
        self.vm_specific = 0
        self.tcp_port = TCP_DATA_UNSECURED
        self.udp_port = UDP_DISCOVERY
        self.activation_type = RoutingActivationRequest.ActivationType.Default
        self.protocol_version = 0x02
        self.use_secure = False
        self.auto_reconnect_tcp = False
        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config

        self.init()

    def init(self):
        self.uds_on_ip_client_thread = QThread()
        self.uds_on_ip_client = QUDSOnIPClient()
        self.uds_on_ip_client.moveToThread(self.uds_on_ip_client_thread)

        self.ui_signal_connect_to_slot()
        self.uds_on_ip_client_signal_connect_to_slot()

        self.uds_on_ip_client_thread.start()
        self.get_ip_list()

    # UI信号连接到槽函数
    def ui_signal_connect_to_slot(self):
        self.pushButton_ConnectDoIP.clicked.connect(self.change_doip_connect_state)
        self.pushButton_SendDoIP.clicked.connect(self.uds_on_ip_client.send)
        self.pushButton_EditConfig.clicked.connect(self.open_edit_config_panel)
        self.pushButton_RefreshIP.clicked.connect(self.get_ip_list)

        self.connect_or_disconnect_doip_signal.connect(self.uds_on_ip_client.change_doip_connect_state)

    def change_doip_connect_state(self):
        self.uds_on_ip_client.ecu_ip_address = self.ecu_ip_address
        self.uds_on_ip_client.ecu_logical_address = self.ecu_logical_address
        self.uds_on_ip_client.tcp_port = self.tcp_port
        self.uds_on_ip_client.udp_port = self.udp_port
        self.uds_on_ip_client.activation_type = self.activation_type
        self.uds_on_ip_client.protocol_version = self.protocol_version
        self.uds_on_ip_client.client_logical_address = self.client_logical_address
        self.uds_on_ip_client.client_ip_address = self.client_ip_address
        self.uds_on_ip_client.use_secure = self.use_secure
        self.uds_on_ip_client.auto_reconnect_tcp = self.auto_reconnect_tcp
        self.uds_on_ip_client.vm_specific = self.vm_specific

        self.uds_on_ip_client.uds_request_timeout = self.uds_request_timeout
        self.uds_on_ip_client.uds_config = self.uds_config

        self.connect_or_disconnect_doip_signal.emit()

    @Slot()
    def open_edit_config_panel(self):
        config_panel = DoIPConfigPanel(parent=self)
        config_panel.lineEdit_DUT_IP.setText(str(self.ecu_ip_address))
        config_panel.lineEdit_TesterLogicalAddress.setText(str(hex(self.client_logical_address)))
        config_panel.lineEdit_DUTLogicalAddress.setText(str(hex(self.ecu_logical_address)))

        config_panel.config_signal.connect(self.set_config)
        config_panel.exec()

    @Slot()
    def set_config(self, config):
        self.client_logical_address = config['tester_logical_address']
        self.ecu_logical_address = config['DUT_logical_address']
        self.ecu_ip_address = config['DUT_ipv4_address']

    # QUDSOnIPClient中的信号连接到槽函数
    def uds_on_ip_client_signal_connect_to_slot(self):
        self.uds_on_ip_client.doip_connect_state.connect(self._doip_connect_state)

    def _doip_connect_state(self, state: bool):
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

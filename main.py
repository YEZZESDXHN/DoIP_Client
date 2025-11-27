import logging.handlers
import sys

import udsoncan
from PySide6.QtCore import QThread, QObject
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.scripts.metaobjectdump import Signal
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import NegativeResponseException, InvalidResponseException, UnexpectedResponseException, Request, services
from udsoncan.client import Client
from udsoncan.services import *

from DoIPToolMainUI import Ui_MainWindow
from UDSOnIP import QUDSOnIPClient

# udsoncan.setup_logging()


logger = logging.getLogger()  # 通常使用模块名作为 Logger 的名字
logger.setLevel(logging.DEBUG)  # 设置 Logger 的最低日志级别为 DEBUG


# 设置日志文件最大大小（字节）和轮转数量
LOG_FILE = 'DoIP_Client.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5  # 保留 5 个轮转的日志文件

# 创建一个 RotatingFileHandler，将日志输出到文件
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'  # 建议指定编码
)

# 创建一个 StreamHandler，将日志输出到控制台
console_handler = logging.StreamHandler()



formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    和 Ui_MainWindow（界面元素定义）。
    """
    def __init__(self):
        super().__init__()

        # 1. 调用生成的 setupUi 方法
        # 这将初始化所有界面元素（按钮、标签等）
        self.setupUi(self)
        self.ecu_ip = '127.0.0.1'
        self.client_ip = '127.0.0.1'
        self.client_logical_address = 101
        self.ecu_logical_address = 200
        self.uds_on_ip_client_thread = QThread()
        self.uds_on_ip_client = QUDSOnIPClient(ecu_ip_address=self.ecu_ip,
                                               client_ip_address=self.client_ip,
                                               ecu_logical_address=self.ecu_logical_address,
                                               client_logical_address=self.client_logical_address)
        self.uds_on_ip_client.moveToThread(self.uds_on_ip_client_thread)

        self.ui_signal_connect_to_slot()
        self.uds_on_ip_client_signal_connect_to_slot()

        self.uds_on_ip_client_thread.start()

    # UI信号连接到槽函数
    def ui_signal_connect_to_slot(self):
        self.pushButton_ConnectDoIP.clicked.connect(self.uds_on_ip_client.change_doip_connect_state)
        self.pushButton_SendDoIP.clicked.connect(self.uds_on_ip_client.send)

    # QUDSOnIPClient中的信号连接到槽函数
    def uds_on_ip_client_signal_connect_to_slot(self):
        self.uds_on_ip_client.doip_connect_state.connect(self._doip_connect_state)

    def _doip_connect_state(self, state: bool):
        if state:
            self.pushButton_ConnectDoIP.setText('已连接')
        else:
            self.pushButton_ConnectDoIP.setText('连接')





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













#
#
# ecu_ip = '127.0.0.1'
# client_ip_address = '127.0.0.1'
# ecu_logical_address = 200
# print('a')
# DoIP_Client = DoIPClient(ecu_ip_address=ecu_ip,
#                          ecu_logical_address=ecu_logical_address,
#                          client_ip_address=client_ip_address,
#                          client_logical_address=100,
#                          vm_specific=0)
# print('b')
# conn = DoIPClientUDSConnector(DoIP_Client)
# # conn.open()
# # conn.send(b'\x10\x01')
# #
# # raw_response = conn.wait_frame(timeout=1)
# # print(raw_response.hex())
# # conn.close()
#
# tester = Client(conn, request_timeout=2)
# tester.open()
# # req = Request(services.DiagnosticSessionControl, subfunction=1)  # control_type=1 --> StartRoutine
# req = Request.from_payload(b'\x10\x01')
# response = tester.send_request(req)
# print()


# with Client(conn, request_timeout=2) as client:
#     try:
#         client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)
#     except NegativeResponseException as e:
#         print('Server refused request:', e.response.code_name)
#     except (InvalidResponseException, UnexpectedResponseException) as e:
#         print('Invalid server response:', e.response.original_payload)
#
# doip_client.close()
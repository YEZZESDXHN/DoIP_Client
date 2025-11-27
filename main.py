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

udsoncan.setup_logging()




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
        self.ecu_ip = '172.16.104.70'
        self.client_ip_address = '172.16.104.54'
        self.ecu_logical_address = 0x773
        self.uds_on_ip_client_thread = QThread()
        self.uds_on_ip_client = QUDSOnIPClient(ecu_ip_address=self.ecu_ip,
                                               client_ip_address=self.client_ip_address,
                                               ecu_logical_address=self.ecu_logical_address)
        self.uds_on_ip_client.moveToThread(self.uds_on_ip_client_thread)

        self.ui_signal_connect_to_slot()
        self.uds_on_ip_client_signal_connect_to_slot()

        self.uds_on_ip_client_thread.start()

    def ui_signal_connect_to_slot(self):
        self.pushButton_ConnectDoIP.clicked.connect(self.uds_on_ip_client.change_doip_connect_state)

    def uds_on_ip_client_signal_connect_to_slot(self):
        self.uds_on_ip_client.doip_connect_state.connect(self.print_doip_state)

    def print_doip_state(self, state: bool):
        print(state)





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















# ecu_ip = '172.16.104.70'
# client_ip_address = '172.16.104.54'
# ecu_logical_address = 0x773
# print('a')
# DoIP_Client = DoIPClient(ecu_ip_address=ecu_ip,
#                          ecu_logical_address=ecu_logical_address,
#                          client_ip_address=client_ip_address,
#                          client_logical_address=0x7e2,
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
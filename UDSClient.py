import logging
import socket
import ssl
from datetime import datetime
from typing import Optional, Any

from PySide6.QtCore import QObject, Signal, Slot
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig, Request, Response, NegativeResponseException, TimeoutException, \
    InvalidResponseException, UnexpectedResponseException, ConfigError
from udsoncan.client import Client
from udsoncan.configs import default_client_config

from user_data import DoIPMessageStruct, MessageDir

logger = logging.getLogger('UDSOnIPClient.' + __name__)


class MyDoIPClient(DoIPClient):
    def __init__(
            self,
            ecu_ip_address,
            ecu_logical_address,
            tcp_port=TCP_DATA_UNSECURED,
            udp_port=UDP_DISCOVERY,
            activation_type=RoutingActivationRequest.ActivationType.Default,
            protocol_version=0x02,
            client_logical_address=0x0E00,
            client_ip_address=None,
            use_secure=False,
            auto_reconnect_tcp=False,
            vm_specific=None,
    ):
        super().__init__(ecu_ip_address,
                         ecu_logical_address,
                         tcp_port,
                         udp_port,
                         activation_type,
                         protocol_version,
                         client_logical_address,
                         client_ip_address,
                         use_secure,
                         auto_reconnect_tcp,
                         vm_specific)

    def _connect(self):
        """Helper to establish socket communication"""
        self._tcp_sock = socket.socket(self._address_family, socket.SOCK_STREAM)
        self._tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self._tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        if self._client_ip_address is not None:
            self._tcp_sock.bind((self._client_ip_address, 0))
        self._tcp_sock.settimeout(2)  # 原库中超时时间写在connect之后，这里修改到之前使其生效
        self._tcp_sock.connect((self._ecu_ip_address, self._tcp_port))
        self._tcp_close_detected = False

        self._udp_sock = socket.socket(self._address_family, socket.SOCK_DGRAM)
        self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._udp_sock.settimeout(2)
        if self._client_ip_address is not None:
            self._udp_sock.bind((self._client_ip_address, 0))

        if self._use_secure:
            if isinstance(self._use_secure, ssl.SSLContext):
                ssl_context = self._use_secure
            else:
                ssl_context = ssl.create_default_context()
            self._wrap_socket(ssl_context)


class QUDSClient(QObject):
    error_signal = Signal(str)
    info_signal = Signal(str)

    doip_connect_state = Signal(bool)

    doip_request = Signal(DoIPMessageStruct)
    doip_response = Signal(DoIPMessageStruct)

    def __init__(self):
        super().__init__()
        self._doip_client = None
        self.uds_on_ip_client = None

        self.ecu_ip_address = None
        self.ecu_logical_address = None
        self.tcp_port = TCP_DATA_UNSECURED
        self.udp_port = UDP_DISCOVERY
        self.activation_type = RoutingActivationRequest.ActivationType.Default
        self.protocol_version = 0x02
        self.client_logical_address = 0x0E00
        self.client_ip_address = None
        self.use_secure = False
        self.auto_reconnect_tcp = False
        self.vm_specific = None

        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config


    @Slot()
    def change_doip_connect_state(self):
        logger.debug('收到触发DoIP连接状态切换信号')
        if self._doip_client and self.uds_on_ip_client:
            logger.debug('开始DoIP连接')
            self.uds_on_ip_client.close()
            self._doip_client = None
            self.uds_on_ip_client = None
            self.doip_connect_state.emit(False)
            logger.info('断开DoIP连接')
        else:
            self.connect_doip()

    def connect_doip(self):
        _doip_client = None
        try:
            self._doip_client = MyDoIPClient(ecu_logical_address=self.ecu_logical_address,
                                             client_logical_address=self.client_logical_address,
                                             client_ip_address=self.client_ip_address,
                                             use_secure=self.use_secure,
                                             ecu_ip_address=self.ecu_ip_address,
                                             tcp_port=self.tcp_port,
                                             udp_port=self.udp_port,
                                             activation_type=self.activation_type,
                                             protocol_version=self.protocol_version,
                                             auto_reconnect_tcp=self.auto_reconnect_tcp,
                                             vm_specific=self.vm_specific,
                                             )
            self.doip_connect_state.emit(True)
            info_message = f'DoIP连接成功'
            logger.info(info_message)
            logger.debug(f'ecu_logical_address={self.ecu_logical_address},'
                         f'client_logical_address={self.client_logical_address},'
                         f'client_ip_address={self.client_ip_address},'
                         f'ecu_ip_address={self.ecu_ip_address},'
                         f'auto_reconnect_tcp={self.auto_reconnect_tcp},'
                         f'vm_specific={self.vm_specific}')
            self.info_signal.emit(info_message)
        except Exception as e:
            error_message = f"DoIP连接失败:{str(e)}"
            logger.exception(str(e))
            self.doip_connect_state.emit(False)
            self.error_signal.emit(error_message)
            return
        if self._doip_client:
            try:
                _conn = DoIPClientUDSConnector(self._doip_client)
                self.uds_on_ip_client = Client(_conn, request_timeout=self.uds_request_timeout,
                                               config=self.uds_config)
                self.uds_on_ip_client.open()
            except Exception as e:
                self._doip_client = None
                self.uds_on_ip_client = None

                self.doip_connect_state.emit(False)
                logger.exception(str(e))
                error_message = f'uds client 创建失败'
                self.info_signal.emit(f"{error_message},{str(e)}")

    def send_payload(self, payload: bytes):
        if self.uds_on_ip_client:
            try:
                req = Request.from_payload(payload)
                req_data = req.get_payload()
                req_table_view_data = DoIPMessageStruct(
                    Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    Dir=MessageDir.Tx,
                    Type=req.service.get_name(),
                    Destination_IP=self.ecu_ip_address,
                    Source_IP=self.client_ip_address,
                    Data_bytes=req_data,
                    DataLength=len(req_data),

                )
                req_table_view_data.update_data_by_data_bytes()

                self.doip_request.emit(req_table_view_data)

                response = self.uds_on_ip_client.send_request(req)
                resp_data = response.original_payload
                resp_table_view_data = DoIPMessageStruct(
                    Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    Dir=MessageDir.Rx,
                    Type=response.code_name,
                    Destination_IP=self.client_ip_address,
                    Source_IP=self.ecu_ip_address,
                    Data_bytes=resp_data,
                    DataLength=len(resp_data),
                    code_name=response.code_name,
                    uds_data=response.data
                )
                resp_table_view_data.update_data_by_data_bytes()
                self.doip_response.emit(resp_table_view_data)
            except TimeoutException as e:
                resp_table_view_data = DoIPMessageStruct(
                    Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    Dir=MessageDir.Rx,
                    Type='TimeoutException',
                )
                self.doip_response.emit(resp_table_view_data)
                self.error_signal.emit(e)
                logger.debug(f'timeout:{str(e)}')
            except NegativeResponseException as negative_response:
                response = negative_response.response
                resp_data = response.original_payload
                resp_table_view_data = DoIPMessageStruct(
                    Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    Dir=MessageDir.Rx,
                    Type=response.code_name,
                    Destination_IP=self.client_ip_address,
                    Source_IP=self.ecu_ip_address,
                    Data_bytes=resp_data,
                    DataLength=len(resp_data),
                    code_name=response.code_name,
                    uds_data=response.data
                )
                resp_table_view_data.update_data_by_data_bytes()
                self.doip_response.emit(resp_table_view_data)
            except InvalidResponseException as e:
                logger.debug(f'InvalidResponseException:{str(e)}')
            except UnexpectedResponseException as e:
                logger.debug(f'UnexpectedResponseException:{str(e)}')
            except ConfigError as e:
                logger.debug(f'ConfigError:{str(e)}')
            except Exception as e:
                try:
                    resp_table_view_data = DoIPMessageStruct(
                        Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        Dir=MessageDir.Rx,
                        Type=e.args[0],
                    )
                    self.doip_response.emit(resp_table_view_data)
                except:
                    pass
                self.error_signal.emit(e)
                logger.exception(str(e))
        else:
            info_message = f'DoIP未连接'
            logger.info(info_message)
            self.info_signal.emit(info_message)


def main():
    ecu_ip = '127.0.0.1'
    client_ip_address = '127.0.0.1'
    client_logical_address = 100
    ecu_logical_address = 200
    uds_client = QUDSOnIPClient()
    uds_client.connect_doip()
    uds_client.send()


if __name__ == "__main__":
    main()

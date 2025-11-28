import logging
from typing import Optional, Any

from PySide6.QtCore import QObject, Signal, Slot
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig, Request
from udsoncan.client import Client
from udsoncan.configs import default_client_config

logger = logging.getLogger('UDSOnIPClient.' + __name__)


class QUDSOnIPClient(QObject):
    error_signal = Signal(str)
    info_signal = Signal(str)

    doip_connect_state = Signal(bool)

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
        if self._doip_client and self.uds_on_ip_client:
            self.uds_on_ip_client.close()
            self._doip_client = None
            self.uds_on_ip_client = None
            self.doip_connect_state.emit(False)
        else:
            self.connect_doip()

    def connect_doip(self):
        _doip_client = None
        try:
            self._doip_client = DoIPClient(ecu_logical_address=self.ecu_logical_address,
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
            self.info_signal.emit(info_message)
        except Exception as e:
            error_message = f"DoIP连接失败:{e}"
            logger.exception(e)
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
                logger.exception(e)
                error_message = f'uds client 创建失败'
                self.info_signal.emit(f"{error_message},{e}")

    def send(self):
        if self.uds_on_ip_client:
            try:
                req = Request.from_payload(b'\x10\x01')
                self.uds_on_ip_client.send_request(req)
            except Exception as e:
                self.error_signal.emit(e)
                self.doip_connect_state.emit(False)
                self._doip_client = None
                self.uds_on_ip_client = None

                logger.exception(e)
        else:
            info_message = f'DoIP未连接，将进行自动连接'
            logger.info(info_message)
            self.info_signal.emit(info_message)
            self.connect_doip()
            req = Request.from_payload(b'\x10\x01')
            self.uds_on_ip_client.send_request(req)


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

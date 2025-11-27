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

logger = logging.getLogger(__name__)


class QUDSOnIPClient(QObject):
    error_signal = Signal(str)
    info_signal = Signal(str)

    doip_connect_state = Signal(bool)

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
            request_timeout: Optional[float] = None,
            config: ClientConfig = default_client_config,
    ):
        super().__init__()
        self._doip_client = None
        self.uds_on_ip_client = None
        self._ecu_logical_address = ecu_logical_address
        self._client_logical_address = client_logical_address
        self._client_ip_address = client_ip_address
        self._use_secure = use_secure
        self._ecu_ip_address = ecu_ip_address
        self._tcp_port = tcp_port
        self._udp_port = udp_port
        self._activation_type = activation_type
        self._protocol_version = protocol_version
        self._auto_reconnect_tcp = auto_reconnect_tcp
        self._vm_specific = vm_specific
        self._uds_request_timeout = request_timeout
        self._uds_config = config

    @Slot()
    def change_doip_connect_state(self):
        if self._doip_client and self.uds_on_ip_client:
            self.uds_on_ip_client.close()
            self.doip_connect_state.emit(False)
        else:
            self.connect_doip()


    def connect_doip(self):
        _doip_client = None
        print('==')
        try:
            self._doip_client = DoIPClient(ecu_logical_address=self._ecu_logical_address,
                                           client_logical_address=self._client_logical_address,
                                           client_ip_address=self._client_ip_address,
                                           use_secure=self._use_secure,
                                           ecu_ip_address=self._ecu_ip_address,
                                           tcp_port=self._tcp_port,
                                           udp_port=self._udp_port,
                                           activation_type=self._activation_type,
                                           protocol_version=self._protocol_version,
                                           auto_reconnect_tcp=self._auto_reconnect_tcp,
                                           vm_specific=self._vm_specific,
                                           )
            print('===')
            self.doip_connect_state.emit(True)
            self.info_signal.emit("DoIP连接成功")
        except Exception as e:
            print('====')
            logger.error(f"DoIP连接失败:{e}", exc_info=True)
            self.doip_connect_state.emit(False)
            self.error_signal.emit(f"DoIP连接失败:{e}")
        if self._doip_client:
            _conn = DoIPClientUDSConnector(self._doip_client)
            self.uds_on_ip_client = Client(_conn, request_timeout=self._uds_request_timeout,
                                           config=self._uds_config)
            self.uds_on_ip_client.open()


def main():
    ecu_ip = '172.16.104.70'
    client_ip_address = '172.16.104.54'
    ecu_logical_address = 0x773
    uds_client = QUDSOnIPClient(ecu_ip_address=ecu_ip,
                                ecu_logical_address=ecu_logical_address,
                                client_ip_address=client_ip_address,
                                client_logical_address=0x7e2,
                                vm_specific=0)
    uds_client.connect_doip()


if __name__ == "__main__":
    main()

import inspect
import logging
import os
import socket
import ssl
import sys
from datetime import datetime
from typing import Optional, Any, runtime_checkable, Protocol

import can
import isotp
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest
from udsoncan import ClientConfig, Request, Response, NegativeResponseException, TimeoutException, \
    InvalidResponseException, UnexpectedResponseException, ConfigError
from udsoncan.client import Client
from udsoncan.configs import default_client_config
import importlib.util

from udsoncan.connections import PythonIsoTpConnection

from app.core.interface_manager import DEFAULT_BIT_TIMING
from app.user_data import DoIPMessageStruct, MessageDir, DoIPConfig, UdsOnCANConfig

logger = logging.getLogger('UDSTool.' + __name__)


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


@runtime_checkable
class GenerateKeyExOptProto(Protocol):
    def __call__(self,
                 seed: bytes,
                 level: int,
                 max_key_size: int = 64,
                 variant: Any = None,
                 options: Any = None) -> Optional[bytes]:
        ...


class QUDSClient(QObject):
    error_signal = Signal(str)
    info_signal = Signal(str)
    warning_signal = Signal(str)

    uds_connect_state = Signal(bool)

    doip_request = Signal(DoIPMessageStruct)
    doip_response = Signal(DoIPMessageStruct)
    uds_response_finished = Signal()

    def __init__(self):
        super().__init__()
        self.conn = None
        self.tp_addr = None
        self.can_notifier = None
        self.can_bus = None
        self.cantp_stack = None
        self.generate_key_func: Optional[GenerateKeyExOptProto] = None
        self.external_security_module = None
        self._uds_client = None
        self.uds_on_ip_client = None

        self.is_can_uds: bool = False
        self.uds_on_can_config = UdsOnCANConfig()
        self.uds_on_ip_config = DoIPConfig()


        # self.ecu_ip_address = None
        # self.ecu_logical_address = None
        # self.tcp_port = TCP_DATA_UNSECURED
        # self.udp_port = UDP_DISCOVERY
        # self.activation_type = RoutingActivationRequest.ActivationType.Default
        # self.protocol_version = 0x02
        # self.client_logical_address = 0x0E00
        self.client_ip_address = None
        self.can_interface = None
        # self.use_secure = False
        self.auto_reconnect_tcp = False
        # self.vm_specific = None
        # self.GenerateKeyExOptPath: Optional[str] = None

        self.uds_request_timeout: Optional[float] = None
        self.uds_config: ClientConfig = default_client_config

        self.tester_present_timer = QTimer(self)
        self.tester_present_timer.timeout.connect(self.send_tester_present)

        self.security_seed: bytes = b''
        self.security_key: bytes = b''

    @Slot(bool)
    def set_tester_present_timer(self, flag: bool):
        if flag:
            self.tester_present_timer.start(3000)
        else:
            self.tester_present_timer.stop()

    def load_generate_key_ex_opt(self, file_path: str) -> bool:
        """
        动态加载外部安全算法脚本
        """
        if not file_path:
            return False
        if not os.path.exists(file_path):
            self.error_signal.emit(f"错误: 找不到算法文件 -> {file_path}")
            logger.error(f"错误: 找不到算法文件 -> {file_path}")
            return False

        # 将脚本目录加入 sys.path
        script_dir = os.path.dirname(os.path.abspath(file_path))
        if script_dir not in sys.path:
            sys.path.append(script_dir)

        try:
            self.info_signal.emit(f"正在加载外部算法: {file_path}")
            logger.debug(f"正在加载外部算法: {file_path}")
            # 1. 动态加载模块
            module_name = "external_security_algo"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                raise ImportError("无法初始化模块加载器")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 2. 获取函数对象
            target_func_name = 'GenerateKeyExOpt'
            if hasattr(module, target_func_name):
                func = getattr(module, target_func_name)

                # 3. 严格的签名检查
                if not callable(func):
                    self.error_signal.emit(f"错误: {target_func_name} 不是一个函数")
                    logger.error(f"错误: {target_func_name} 不是一个函数")
                    return False

                sig = inspect.signature(func)
                params = list(sig.parameters.values())
                if len(params) != 5:
                    self.error_signal.emit(f"校验失败: 函数参数不足,{params}")
                    logger.error(f"校验失败: 函数参数不足,{params}")
                    return False

                # 4. 加载成功
                self.external_security_module = module  # 保持引用
                self.generate_key_func = func  # 赋值
                self.info_signal.emit("成功加载 GenerateKeyExOpt 算法")
                logger.debug("成功加载 GenerateKeyExOpt 算法")
                return True
            else:
                self.error_signal.emit(f"警告: 脚本中未找到函数 {target_func_name}")
                logger.error(f"警告: 脚本中未找到函数 {target_func_name}")
                return False

        except Exception as e:
            self.error_signal.emit(f"加载脚本时发生异常: {e}")
            logger.exception(f"加载脚本时发生异常: {e}")
            return False

    def execute_security_access(self,
                                seed: bytes,
                                level: int,
                                max_key_size: int = 64,
                                variant: Any = None,
                                options: Any = None) -> Optional[bytes]:
        """
        调用已加载的算法计算 Key
        """
        if not self.generate_key_func:
            self.warning_signal.emit("错误: 未加载安全算法，无法计算 Key")
            return None

        try:
            self.info_signal.emit(f"正在计算 Key (Seed: {seed.hex(' ')}, Level: {level})")

            # 这里完全匹配你定义的签名
            key = self.generate_key_func(
                seed=seed,
                max_key_size=max_key_size,
                level=level,
                variant=variant,
                options=options
            )

            # 结果校验
            if key is None:
                self.error_signal.emit("算法返回了 None")
                return None

            if not isinstance(key, (bytes, bytearray)):
                self.error_signal.emit(f"算法返回类型错误: 期望 bytes, 实际是 {type(key)}")
                return None
            self.info_signal.emit(f"计算完成,key: {key.hex(' ')}")
            return bytes(key)

        except Exception as e:
            self.error_signal.emit(f"算法执行期间崩溃: {str(e)}")
            logger.exception(f"算法执行期间崩溃: {str(e)}")
            return None

    @Slot()
    def change_uds_connect_state(self):
        logger.debug('收到触发DoIP连接状态切换信号')
        if self.uds_on_ip_client:
            self.disconnect_uds()
        else:
            self.connect_uds()

    def disconnect_uds(self):
        if self.is_can_uds:
            self.uds_on_ip_client.close()
            self.conn.close()
            self.cantp_stack.stop()
            self.can_notifier.stop(2)
            self.can_bus.shutdown()
        else:
            self.uds_on_ip_client.close()
            self.conn.close()

        self._uds_client = None
        self.conn = None
        self.uds_on_ip_client = None
        self.cantp_stack = None
        self.can_notifier = None
        self.can_bus = None
        self.uds_connect_state.emit(False)
        info_message = f'DoIP断开连接'
        logger.info(info_message)

    def isotp_error_handler(self, error):
        print(f"isotp error:{error}")


    def init_can_bus(self, can_channel, timing=DEFAULT_BIT_TIMING) -> can.Bus:
        try:
            logger.debug(f"[*] 正在连接到 {can_channel['interface']} (通道: {can_channel['channel']}) ...")

            # 初始化 Bus 对象
            # **target_config 会将字典解包为关键字参数传入
            can_bus = can.Bus(**can_channel, timing=timing)

            logger.debug(f"[+] 连接成功！总线状态: {can_bus.state}")
            return can_bus
        except Exception as e:
            try:
                can_bus = can.Bus(**can_channel)
                logger.error(f"[+] {str(e)}，总线状态: {can_bus.state}")
                return can_bus
            except Exception as e:
                logger.exception(f"[-] 连接失败: {str(e)}")
                return None

    def connect_uds(self):
        if self.is_can_uds:
            try:
                isotpparams = {
                    'blocking_send': False,
                    'stmin': 32,
                    # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
                    'blocksize': 8,
                    # Request the sender to send 8 consecutives frames before sending a new flow control message
                    'wftmax': 0,  # Number of wait frame allowed before triggering an error
                    'tx_data_length': 8,  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
                    # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
                    'tx_data_min_length': 8,
                    'tx_padding': 0,  # Will pad all transmitted CAN messages with byte 0x00.
                    'rx_flowcontrol_timeout': 1000,
                    # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
                    'rx_consecutive_frame_timeout': 1000,
                    # Time in seconds to wait between consecutive frames when transmitting.
                    # When set, this value will override the receiver stmin requirement.
                    # When None, the receiver stmin parameter will be respected.
                    # This parameter can be useful to speed up a transmission by setting a value of 0 (send as fast as possible)
                    # on a system that has low execution priority or coarse thread resolution
                    'override_receiver_stmin': 0,
                    # 传输时连续帧之间等待的时间（以秒为单位）。
                    # 设置后，此值将覆盖接收器stmin要求。当 时None，将遵守接收器 stmin参数。
                    # 在执行优先级较低或线程分辨率较粗的系统上，通过将此参数设置为 0（尽可能快地发送），可以加快传输速度。
                    'max_frame_size': 4095,  # Limit the size of receive frame.
                    'can_fd': True,
                    # Does not set the can_fd flag on the output CAN messages
                    'bitrate_switch': False,  # Does not set the bitrate_switch flag on the output CAN messages
                    'rate_limit_enable': False,  # Disable the rate limiter
                    'rate_limit_max_bitrate': 1000000,
                    # Ignored when rate_limit_enable=False. Sets the max bitrate when rate_limit_enable=True
                    'rate_limit_window_size': 0.2,
                    # Ignored when rate_limit_enable=False. Sets the averaging window size for bitrate calculation when rate_limit_enable=True
                    'listen_mode': False,  # Does not use the listen_mode which prevent transmission.
                }
                self.can_bus = self.init_can_bus(self.can_interface)
                self.can_notifier = can.Notifier(self.can_bus, [can.Printer()])
                self.tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=123, rxid=456,
                                        functional_id=789)
                self.cantp_stack = isotp.NotifierBasedCanStack(bus=self.can_bus, notifier=self.can_notifier, address=self.tp_addr,
                                                               params=isotpparams,
                                                               error_handler=self.isotp_error_handler)

                self.conn = PythonIsoTpConnection(self.cantp_stack)
                self.uds_on_ip_client = Client(self.conn, request_timeout=self.uds_request_timeout,
                                               config=self.uds_config)
                self.uds_on_ip_client.open()

                self.uds_connect_state.emit(True)
                info_message = f'cantp_stack连接成功'
                logger.info(info_message)
            except Exception as e:
                error_message = f"UDS on CAN连接失败:{str(e)}"
                self.uds_connect_state.emit(False)
                self.error_signal.emit(error_message)
                logger.exception(str(e))
                self._uds_client = None
                self.uds_on_ip_client = None
                self.cantp_stack = None
                self.can_notifier = None
                self.can_bus = None
                self.conn = None
                return
        else:
            try:
                self._uds_client = MyDoIPClient(ecu_logical_address=self.uds_on_ip_config.dut_logical_address,
                                                client_logical_address=self.uds_on_ip_config.tester_logical_address,
                                                client_ip_address=self.client_ip_address,
                                                use_secure=self.uds_on_ip_config.use_secure,
                                                ecu_ip_address=self.uds_on_ip_config.dut_ipv4_address,
                                                tcp_port=self.uds_on_ip_config.tcp_port,
                                                udp_port=self.uds_on_ip_config.udp_port,
                                                activation_type=self.uds_on_ip_config.activation_type,
                                                protocol_version=self.uds_on_ip_config.protocol_version,
                                                auto_reconnect_tcp=self.auto_reconnect_tcp,
                                                vm_specific=self.uds_on_ip_config.oem_specific,
                                                )
                self.conn = DoIPClientUDSConnector(self._uds_client)
                self.uds_on_ip_client = Client(self.conn, request_timeout=self.uds_request_timeout,
                                               config=self.uds_config)
                self.uds_on_ip_client.open()
                self.uds_connect_state.emit(True)
                info_message = f'DoIP连接成功'
                logger.info(info_message)
                logger.debug(f'ecu_logical_address={self.uds_on_ip_config.dut_logical_address,},'
                             f'client_logical_address={self.uds_on_ip_config.tester_logical_address,},'
                             f'client_ip_address={self.client_ip_address},'
                             f'ecu_ip_address={self.uds_on_ip_config.dut_ipv4_address,},'
                             f'auto_reconnect_tcp={self.auto_reconnect_tcp},'
                             f'vm_specific={self.uds_on_ip_config.oem_specific,}')
                self.info_signal.emit(info_message)
            except Exception as e:
                error_message = f"DoIP连接失败:{str(e)}"
                self.uds_connect_state.emit(False)
                self.error_signal.emit(error_message)
                logger.exception(str(e))
                self._uds_client = None
                self.uds_on_ip_client = None
                self.cantp_stack = None
                self.can_notifier = None
                self.can_bus = None
                self.conn = None
                return

    def _handle_exceptions(self, e: Exception, prefix: str, display_trace) -> Optional[Response]:
        """
        统一处理 UDS 通讯过程中的各类异常
        :param e: 捕获到的异常对象
        :param prefix: 日志前缀，例如 "" 或 "TF:"
        """
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # 1. 针对已知特定异常的处理
        if isinstance(e, TimeoutException):
            resp_struct = DoIPMessageStruct(
                Time=time_str,
                Dir=MessageDir.Rx,
                Type='TimeoutException',
            )
            if display_trace == 1:
                self.doip_response.emit(resp_struct)
            self.error_signal.emit(str(e))
            logger.debug(f'{prefix}timeout:{str(e)}')

        elif isinstance(e, NegativeResponseException):
            # 提取负响应中的原始数据
            response = e.response
            if self.is_can_uds:
                tester_id = self.uds_on_can_config.req_id
                dut_id = self.uds_on_can_config.resp_id
            else:
                tester_id = self.uds_on_ip_config.tester_logical_address
                dut_id = self.uds_on_ip_config.dut_logical_address
            resp_struct = self._create_message_struct(
                msg_dir=MessageDir.Rx,
                msg_type=response.code_name,
                data=response.original_payload,
                tx_id=dut_id,
                rx_id=tester_id,
                extra={"code_name": response.code_name, "uds_data": response.data}
            )
            if display_trace == 1:
                self.doip_response.emit(resp_struct)
            return response

        elif isinstance(e, InvalidResponseException):
            logger.exception(f'{prefix}{type(e).__name__}:{str(e)}')
        elif isinstance(e, UnexpectedResponseException):
            logger.exception(f'{prefix}{type(e).__name__}:{str(e)}')
        elif isinstance(e, ConfigError):
            logger.exception(f'{prefix}{type(e).__name__}:{str(e)}')
        elif isinstance(e, (OSError, socket.timeout)):
            self.disconnect_uds()
            self.error_signal.emit(str(e))
            logger.exception(f'{prefix}{type(e).__name__}:{str(e)}')
        else:
            self.error_signal.emit(str(e))
            logger.exception(f"{prefix}{str(e)}")
        self.uds_response_finished.emit()

    def _execute_uds_request(self, payload: bytes, log_prefix: str = "", display_trace=1) -> Optional[Response]:
        """
        核心方法：处理所有 UDS 请求的发送、响应解析、信号发射和异常捕获
        """
        if not self.uds_on_ip_client:
            message = f"{log_prefix}DoIP未连接"
            logger.info(message)
            self.uds_response_finished.emit()
            self.info_signal.emit(message)
            return None

        try:
            # 1. 构造并发送请求
            req = Request.from_payload(payload)

            try:
                req_data = req.get_payload()
            except Exception as e:
                logger.warning(f'从Request获取req date失败')
                req = None
                req_data = payload
            if self.is_can_uds:
                tester_id = self.uds_on_can_config.req_id
                dut_id = self.uds_on_can_config.resp_id
            else:
                tester_id = self.uds_on_ip_config.tester_logical_address
                dut_id = self.uds_on_ip_config.dut_logical_address

            req_struct = self._create_message_struct(
                msg_dir=MessageDir.Tx,
                msg_type=req.service.get_name() if req else 'Raw date req',
                data=req_data,
                tx_id=tester_id,
                rx_id=dut_id
            )
            if not self.is_can_uds:
                req_struct.Destination_IP = self.uds_on_ip_config.dut_ipv4_address
                if self.client_ip_address:
                    req_struct.Source_IP = self.client_ip_address
            if display_trace == 1:
                self.doip_request.emit(req_struct)
            if req:
                # 2. 执行请求
                response = self.uds_on_ip_client.send_request(req)
                if req.suppress_positive_response:
                    self.uds_response_finished.emit()
                if not hasattr(response, 'original_payload'):
                    return response
                if len(response.original_payload) > 1 and \
                        response.original_payload[0] == 0x67 and \
                        response.original_payload[1] % 2 == 1:
                    self.security_seed = response.original_payload[2:]
                    self.security_key = self.execute_security_access(seed=self.security_seed,
                                                                     level=response.original_payload[1])

                # 3. 处理正常响应
                resp_struct = self._create_message_struct(
                    msg_dir=MessageDir.Rx,
                    msg_type=response.code_name,
                    data=response.original_payload,
                    extra={"code_name": response.code_name, "uds_data": response.data},
                    tx_id=dut_id,
                    rx_id=tester_id
                )

            else:
                self.uds_on_ip_client.conn.send(req_data)
                response = self.uds_on_ip_client.conn.wait_frame(timeout=1)
                if not response:
                    self.uds_response_finished.emit()
                    return response
                resp_struct = self._create_message_struct(
                    msg_dir=MessageDir.Rx,
                    msg_type='Raw date response',
                    data=response,
                    tx_id=dut_id,
                    rx_id=tester_id
                )

            if not self.is_can_uds:
                resp_struct.Destination_IP = self.uds_on_ip_config.dut_ipv4_address
                if self.client_ip_address:
                    resp_struct.Source_IP = self.client_ip_address
            if display_trace == 1:
                self.doip_response.emit(resp_struct)
            self.uds_response_finished.emit()
            return response

        except (
                TimeoutException,
                NegativeResponseException,
                InvalidResponseException,
                UnexpectedResponseException,
                ConfigError,
                Exception) as e:
            ret = self._handle_exceptions(e, log_prefix, display_trace)
            if isinstance(ret, Response):
                return ret
            else:
                return None

    def _create_message_struct(self, msg_dir, msg_type, data, tx_id, rx_id, extra=None):
        """辅助方法：统一创建消息结构体"""
        struct = DoIPMessageStruct(
            Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            Dir=msg_dir,
            Type=msg_type,
            Data_bytes=data,
            DataLength=len(data) if data else 0,
            TX_id=tx_id,
            RX_id=rx_id
        )
        if extra:
            for key, value in extra.items():
                setattr(struct, key, value)

        struct.update_data_by_data_bytes()
        return struct

    def send_payload(self, payload: bytes, display_trace=1) -> Optional[Response]:
        """内部调用的原方法"""
        return self._execute_uds_request(payload=payload, display_trace=display_trace)

    @Slot()
    def send_tester_present(self):
        """内部调用的原方法"""
        if self._uds_client and self.uds_on_ip_client:
            payload = b'\x3e\x80'
            self._execute_uds_request(payload)


def main():
    ecu_ip = '127.0.0.1'
    client_ip_address = '127.0.0.1'
    client_logical_address = 100
    ecu_logical_address = 200
    uds_client = QUDSClient()
    uds_client.connect_uds()
    uds_client.send_payload()


if __name__ == "__main__":
    main()

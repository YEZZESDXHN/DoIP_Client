import inspect
import logging
import os
import socket
import ssl
import sys
from datetime import datetime
from typing import Optional, Any, runtime_checkable, Protocol

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

from user_data import DoIPMessageStruct, MessageDir

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


    doip_connect_state = Signal(bool)

    doip_request = Signal(DoIPMessageStruct)
    doip_response = Signal(DoIPMessageStruct)
    uds_response_finished = Signal()

    def __init__(self):
        super().__init__()
        self.generate_key_func: Optional[GenerateKeyExOptProto] = None
        self.external_security_module = None
        self._uds_client = None
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
        self.GenerateKeyExOptPath: Optional[str] = None

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

    def execute_security_access(self, seed: bytes, level: int, max_key_size: int = 64, variant: Any = None, options: Any = None) -> Optional[bytes]:
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
        if self._uds_client and self.uds_on_ip_client:
            self.disconnect_uds()
            self.doip_connect_state.emit(False)
            logger.info('断开DoIP连接')
        else:
            self.connect_uds()
    def disconnect_uds(self):
        self.uds_on_ip_client.close()
        self._uds_client = None
        self.uds_on_ip_client = None
        self.doip_connect_state.emit(False)

    def connect_uds(self):
        try:
            self._uds_client = MyDoIPClient(ecu_logical_address=self.ecu_logical_address,
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
        if self._uds_client:
            try:
                _conn = DoIPClientUDSConnector(self._uds_client)
                self.uds_on_ip_client = Client(_conn, request_timeout=self.uds_request_timeout,
                                               config=self.uds_config)
                self.uds_on_ip_client.open()
            except Exception as e:
                self._uds_client = None
                self.uds_on_ip_client = None

                self.doip_connect_state.emit(False)
                logger.exception(str(e))
                error_message = f'uds client 创建失败'
                self.info_signal.emit(f"{error_message},{str(e)}")

    def _handle_exceptions(self, e: Exception, prefix: str) -> Optional[Response]:
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
            self.doip_response.emit(resp_struct)
            self.error_signal.emit(e)
            logger.debug(f'{prefix}timeout:{str(e)}')

        elif isinstance(e, NegativeResponseException):
            # 提取负响应中的原始数据
            response = e.response
            resp_struct = self._create_message_struct(
                msg_dir=MessageDir.Rx,
                msg_type=response.code_name,
                data=response.original_payload,
                dest=self.client_ip_address,
                src=self.ecu_ip_address,
                extra={"code_name": response.code_name, "uds_data": response.data}
            )
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

    def _execute_uds_request(self, payload: bytes, log_prefix: str = "") -> Optional[Response]:
        """
        核心方法：处理所有 UDS 请求的发送、响应解析、信号发射和异常捕获
        """
        if not self.uds_on_ip_client:
            message = f"{log_prefix}DoIP未连接"
            logger.info(message)
            self.info_signal.emit(message)
            return None

        try:
            # 1. 构造并发送请求
            req = Request.from_payload(payload)
            req_data = req.get_payload()

            req_struct = self._create_message_struct(
                msg_dir=MessageDir.Tx,
                msg_type=req.service.get_name(),
                data=req_data,
                dest=self.ecu_ip_address,
                src=self.client_ip_address
            )
            self.doip_request.emit(req_struct)

            # 2. 执行请求
            response = self.uds_on_ip_client.send_request(req)
            if not hasattr(response, 'original_payload'):
                return response
            if len(response.original_payload) > 1 and response.original_payload[0] == 0x67 and response.original_payload[1] % 2 == 1:
                self.security_seed = response.original_payload[2:]
                self.security_key = self.execute_security_access(seed=self.security_seed,
                                                                 level=response.original_payload[1])

            # 3. 处理正常响应
            resp_struct = self._create_message_struct(
                msg_dir=MessageDir.Rx,
                msg_type=response.code_name,
                data=response.original_payload,
                dest=self.client_ip_address,
                src=self.ecu_ip_address,
                extra={"code_name": response.code_name, "uds_data": response.data}
            )
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
            ret = self._handle_exceptions(e, log_prefix)
            if isinstance(ret, Response):
                return ret
            else:
                return None

    def _create_message_struct(self, msg_dir, msg_type, data, dest, src, extra=None):
        """辅助方法：统一创建消息结构体"""
        struct = DoIPMessageStruct(
            Time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            Dir=msg_dir,
            Type=msg_type,
            Destination_IP=dest,
            Source_IP=src,
            Data_bytes=data,
            DataLength=len(data) if data else 0,
        )
        if extra:
            for key, value in extra.items():
                setattr(struct, key, value)
        struct.update_data_by_data_bytes()
        return struct

    def send_payload(self, payload: bytes) -> Optional[Response]:
        """内部调用的原方法"""
        return self._execute_uds_request(payload)

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

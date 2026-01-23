import logging
import pprint
from enum import Enum
from typing import Dict, List, Optional

import can
import ifaddr
from PySide6.QtCore import QObject, Signal
from can import BitTiming, BitTimingFd

logger = logging.getLogger('UDSTool.' + __name__)

DEFAULT_BIT_TIMING = BitTiming.from_sample_point(f_clock=16_000_000, bitrate=500_000)


DEFAULT_BIT_TIMING_FD = BitTimingFd.from_sample_point(
    f_clock=80_000_000,
    nom_bitrate=500_000,
    nom_sample_point=80.0,
    data_bitrate=2000_000,
    data_sample_point=80.0,

)

can.interfaces.BACKENDS['tosun'] = ('tosun', 'TSMasterApiBus')
can.interfaces.VALID_INTERFACES = frozenset(sorted(can.interfaces.BACKENDS.keys()))
can.util.VALID_INTERFACES = can.interfaces.VALID_INTERFACES


class CANInterfaceName(str, Enum):
    vector = "vector"
    tosun = "tosun"
    #
    # kvaser = "kvaser"
    # socketcan = "socketcan"
    # serial = "serial"
    # pcan = "pcan"
    # usb2can = "usb2can"
    # ixxat = "ixxat"
    # nican = "nican"
    # iscan = "iscan"
    # virtual = "virtual"
    # udp_multicast = "udp_multicast"
    # neovi = "neovi"
    # slcan = "slcan"
    # robotell = "robotell"
    # canalystii = "canalystii"
    # systec = "systec"
    # seeedstudio = "seeedstudio"
    # cantact = "cantact"
    # gs_usb = "gs_usb"
    # nixnet = "nixnet"
    # neousys = "neousys"
    # etas = "etas"
    # socketcand = "socketcand"


class InterfaceManager(QObject):
    signal_interface_channels = Signal(object)

    def __init__(self):
        super().__init__()
        self.interface_channels = []
        self.is_can_interface = False
        self.can_interface_name: Optional[CANInterfaceName] = None
        self.can_interface_manager = CanInterfaceManager()
        self.eth_interface_manager = EthInterfaceManager()

    def scan_interfaces(self):
        if self.is_can_interface:
            try:
                if self.can_interface_name:
                    self.interface_channels = self.can_interface_manager.scan_devices(self.can_interface_name)
                else:
                    self.interface_channels = []
            except Exception as e:
                logger.exception(e)
                self.interface_channels = []
        else:
            try:
                self.interface_channels = self.eth_interface_manager.get_ethernet_ips()
            except Exception as e:
                logger.exception(e)
                self.interface_channels = []
        self.signal_interface_channels.emit(self.interface_channels)

class EthInterfaceManager:
    def __init__(self):
        pass

    def get_ethernet_ips(self) -> List:
        """
        获取当前电脑上所有被识别为有线连接 (Ethernet) 的网卡 IPv4 地址。

        Returns:
            一个字典，键是网卡名称，值是其 IPv4 地址列表 (不包含 CIDR 前缀)。
            示例: {'Ethernet': ['172.16.10.5'], 'eth0': ['192.168.1.10']}
        """
        # 常见的以太网接口名称关键词 (需要根据具体操作系统调整)
        ETHERNET_KEYWORDS = [
            'eth',  # Linux/Unix/macOS (e.g., eth0, en0)
            'ethernet',  # Windows/macOS (e.g., Ethernet, enpXsY)
            'lan',  # Local Area Network
            'cable',  # Cable connection
            'pci',  # PCI network card
            'local area connection',  # Windows (old/localized names)
            'loopback'
        ]
        ethernet_ips = {}

        try:
            adapters = ifaddr.get_adapters()

            for adapter in adapters:
                # 1. 过滤回环地址
                # if adapter.nice_name.lower() in ('loopback', 'lo'):
                #     continue

                # 2. 检查名称是否包含以太网关键词 (大小写不敏感)
                is_ethernet = False
                for keyword in ETHERNET_KEYWORDS:
                    if keyword in adapter.nice_name.lower():
                        is_ethernet = True
                        break

                # 如果适配器名称被识别为有线接口
                if is_ethernet:
                    ips_v4 = []

                    # 3. 遍历IP地址，只获取IPv4
                    for ip in adapter.ips:
                        # 检查是否是IPv4，并且地址不是回环地址（127.x.x.x）
                        # if ip.is_IPv4 and not ip.ip.startswith('127.'):
                        if ip.is_IPv4:
                            # 只返回IP地址，不带CIDR前缀
                            ips_v4 = ip.ip

                    # 4. 记录有效地址
                    if ips_v4:
                        ethernet_ips[adapter.nice_name] = ips_v4

        except Exception as e:
            print(f"获取网卡信息失败: {str(e)}")
            return []

        return list(ethernet_ips.items())


class CanInterfaceManager(QObject):
    """
    CAN 管理器：负责设备扫描、连接建立以及数据发送。
    """
    signal_interface_channels = Signal(object)

    def __init__(self):
        super().__init__()
        self.available_configs = []
        self.bus = None  # 当前连接的 CAN 总线对象

    def scan_devices(self, interfaces=None):
        """
        扫描可用通道。
        :param interfaces: 字符串列表，例如 ['vector', 'pcan']。
                                  如果为 None，则扫描所有支持的接口。
        """
        if interfaces:
            print(f"[*] 正在仅扫描以下接口: {interfaces} ...")
        else:
            print("[*] 正在扫描所有支持的接口...")

        # 传入 interfaces 参数进行过滤
        self.available_configs = can.detect_available_configs(interfaces=interfaces)
        self.signal_interface_channels.emit(self.available_configs)
        return self.available_configs

    def print_devices(self):
        """打印扫描到的设备列表"""
        if not self.available_configs:
            print("[-] 未发现可用设备。")
            return

        print(f"[+] 发现 {len(self.available_configs)} 个设备:")
        for idx, cfg in enumerate(self.available_configs):
            print(f"    ID {idx}: {cfg['interface']}  - channel {cfg['channel']}")

    def init_can_bus(self, index: int, timing) -> can.Bus:
        if not self.available_configs:
            print("[-] 列表为空，请先执行扫描 (scan_devices)。")
            return None

        if index < 0 or index >= len(self.available_configs):
            print(f"[-] 无效的索引: {index}")
            return None

        target_config = self.available_configs[index]

        try:
            print(f"[*] 正在连接到 {target_config['interface']} (通道: {target_config['channel']}) ...")

            # 初始化 Bus 对象
            # **target_config 会将字典解包为关键字参数传入
            can_bus = can.Bus(**target_config, timing=timing)

            print(f"[+] 连接成功！总线状态: {can_bus.state}")
            self.bus = can_bus
            return can_bus
        except Exception as e:
            print(f"[-] 连接失败: {e}")
            return None

    def connect(self, device_index=0, timing=DEFAULT_BIT_TIMING_FD):
        """
        连接到指定索引的设备。
        :param device_index: scan_devices 结果列表中的索引
        :param bitrate: 波特率 (例如 250000, 500000)
        :return: 成功返回 True，失败返回 False
        """
        if not self.available_configs:
            print("[-] 列表为空，请先执行扫描 (scan_devices)。")
            return False

        if device_index < 0 or device_index >= len(self.available_configs):
            print(f"[-] 无效的索引: {device_index}")
            return False

        # 获取配置字典 (如 {'interface': 'vector', 'channel': 0})
        target_config = self.available_configs[device_index]

        try:
            print(f"[*] 正在连接到 {target_config['interface']} (通道: {target_config['channel']}) ...")

            # 初始化 Bus 对象
            # **target_config 会将字典解包为关键字参数传入
            self.bus = can.Bus(**target_config, timing=timing)

            print(f"[+] 连接成功！总线状态: {self.bus.state}")
            return True
        except Exception as e:
            print(f"[-] 连接失败: {e}")
            return False

    def send_frame(self, arbitration_id, data, is_extended_id=False):
        """
        发送 CAN 帧。
        :param arbitration_id: CAN ID (整数)
        :param data: 数据列表 (例如 [0x01, 0x02])，最大 8 字节
        :param is_extended_id: 是否为扩展帧 (29位 ID)
        """
        if self.bus is None:
            print("[-] 发送失败: 未连接到总线。")
            return

        try:
            # 构建消息
            msg = can.Message(
                arbitration_id=arbitration_id,
                data=data,
                is_extended_id=is_extended_id,
                check=True  # 检查数据长度等参数是否合法
            )

            # 发送消息
            self.bus.send(msg)
            print(f"[>] 发送成功: ID=0x{arbitration_id:X} Data={data}")

        except can.CanError as e:
            print(f"[-] 发送错误: {e}")

    def close(self):
        """关闭总线连接"""
        if self.bus:
            self.bus.shutdown()
            self.bus = None
            print("[*] 连接已关闭。")


if __name__ == "__main__":
    manager = InterfaceManager()
    manager.is_can_interface = True
    manager.can_interface_name = CANInterfaceName.tosun

    manager.scan_interfaces()

    manager.can_interface_manager.print_devices()
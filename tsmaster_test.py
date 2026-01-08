from enum import Enum

import can
import time

from can import BitTiming, BitTimingFd

can.interfaces.BACKENDS['tosun'] = ('tosun', 'TSMasterApiBus')


class CANInterfaceName(str, Enum):
    kvaser = "kvaser"
    socketcan = "socketcan"
    serial = "serial"
    pcan = "pcan"
    usb2can = "usb2can"
    ixxat = "ixxat"
    nican = "nican"
    iscan = "iscan"
    virtual = "virtual"
    udp_multicast = "udp_multicast"
    neovi = "neovi"
    vector = "vector"
    slcan = "slcan"
    robotell = "robotell"
    canalystii = "canalystii"
    systec = "systec"
    seeedstudio = "seeedstudio"
    cantact = "cantact"
    gs_usb = "gs_usb"
    nixnet = "nixnet"
    neousys = "neousys"
    etas = "etas"
    socketcand = "socketcand"
    tosun = "tosun"


DEFAULT_BIT_TIMING = BitTiming.from_sample_point(f_clock=16_000_000, bitrate=500_000)


DEFAULT_BIT_TIMING_FD = BitTimingFd.from_sample_point(
    f_clock=80_000_000,
    nom_bitrate=500_000,
    nom_sample_point=80.0,
    data_bitrate=2000_000,
    data_sample_point=80.0,

)


class CanManager:
    """
    CAN 管理器：负责设备扫描、连接建立以及数据发送。
    """

    def __init__(self):
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
        return self.available_configs

    def print_devices(self):
        """打印扫描到的设备列表"""
        if not self.available_configs:
            print("[-] 未发现可用设备。")
            return

        print(f"[+] 发现 {len(self.available_configs)} 个设备:")
        for idx, cfg in enumerate(self.available_configs):
            print(f"    ID {idx}: {cfg['interface']} -num {cfg['serial']}  - channel {cfg['channel']}")

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


# --- 使用示例 ---
if __name__ == "__main__":
    manager = CanManager()

    # 1. 扫描设备
    print("--- 步骤 1: 扫描设备 ---")
    manager.scan_devices(CANInterfaceName.tosun)
    manager.print_devices()

    # 如果有设备，则连接第一个设备进行测试
    if manager.available_configs:

        # 2. 连接设备 (这里默认连接 ID 0，波特率 500k)
        print("\n--- 步骤 2: 连接设备 ---")
        if manager.connect(device_index=0, timing=DEFAULT_BIT_TIMING_FD):
            # 3. 发送标准帧 (Standard ID)
            # 例如：ID 0x123, 数据 [0x11, 0x22, 0x33]
            print("\n--- 步骤 3: 发送数据 ---")
            manager.send_frame(0x123, [0x11, 0x22, 0x33])

            # 3.1 发送扩展帧 (Extended ID)
            # 例如：ID 0x18DAF110 (UDS 诊断常用来着), 数据 [0x02, 0x10, 0x01]
            manager.send_frame(0x18DAF110, [0x02, 0x10, 0x01], is_extended_id=True)

            # 简单延时，确保数据发完
            time.sleep(0.5)

            # 4. 关闭连接
            print("\n--- 步骤 4: 断开连接 ---")
            manager.close()
    else:
        print("\n未检测到硬件，无法演示发送功能。")

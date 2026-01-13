import logging
from typing import Optional

import can
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from can import BitTiming, BitTimingFd
from pydantic import BaseModel, field_validator, field_serializer
from enum import Enum

from app.core.interface_manager import CANInterfaceName, InterfaceManager
from app.ui.IGPanelUI import Ui_IG

logger = logging.getLogger('UDSTool.' + __name__)

CAN_IG_DEFAULT_BIT_TIMING = BitTiming.from_sample_point(f_clock=16_000_000, bitrate=500_000)


CAN_IG_DEFAULT_BIT_TIMING_FD = BitTimingFd.from_sample_point(
    f_clock=80_000_000,
    nom_bitrate=500_000,
    nom_sample_point=80.0,
    data_bitrate=2000_000,
    data_sample_point=80.0,

)
class MessageType(str, Enum):
    CAN = "CAN"
    CAN_Remote = "CAN_Remote"
    CANFD = "CANFD"
    Extended_CAN = "Extended_CAN"
    Extended_CAN_Remote = "Extended_CAN_Remote"
    Extended_CANFD = "Extended_CANFD"


class CanIgMessages(BaseModel):
    send: bool = False
    trigger: int = 0
    id: int = 0
    type: MessageType = MessageType.CAN
    data_length: int = 8
    brs: bool = False
    data: bytes = b''

    @field_serializer('data')
    def serialize_data(self, data: bytes, _info):
        return data.hex().upper()

    @field_validator('data', mode='before')
    def validate_data(cls, v):
        # Pydantic 在校验类型前会先运行这个函数
        # v 就是从 JSON 里拿到的那个字符串，比如 "FF00"
        if isinstance(v, str):
            try:
                # 将 Hex 字符串转回二进制
                return bytes.fromhex(v)
            except ValueError:
                # 如果字符串不是合法的 Hex，可以选择报错或返回空
                raise ValueError("数据格式错误: 必须是有效的 Hex 字符串")
        return v


class CANIGPanel(Ui_IG, QWidget):
    signal_scan_can_devices = Signal(str)

    def __init__(self, interface_manager, parent=None):
        super().__init__(parent)
        self.can_bus: Optional[can.Bus] = None
        self.current_can_interface = None
        self.can_interface_channels = None
        self.bus_connect_state: bool = False

        self.ig_messages: list[CanIgMessages] = []

        self.setupUi(self)
        self.interface_manager: InterfaceManager = interface_manager
        self._ui_init()

        self._signal_init()

    def _ui_init(self):
        self.comboBox_NMHardwareType.addItems(list(CANInterfaceName))

    def _signal_init(self):
        self.pushButton_NMRefreshCANChannel.clicked.connect(self.scan_can_devices)
        self.signal_scan_can_devices.connect(self.interface_manager.can_interface_manager.scan_devices)
        self.interface_manager.can_interface_manager.signal_interface_channels.connect(self.update_channels)
        self.pushButton_NMConnectCANBus.clicked.connect(self.init_can_bus)

        self.pushButton_NMRefreshCANChannel.clicked.emit()

    def scan_can_devices(self):
        current_text = self.comboBox_NMHardwareType.currentText()
        self.signal_scan_can_devices.emit(current_text)

    def init_can_bus(self, can_channel, timing=CAN_IG_DEFAULT_BIT_TIMING_FD):
        try:
            logger.debug(f"[*] 正在连接到 {can_channel['interface']} (通道: {can_channel['channel']}) ...")

            # 初始化 Bus 对象
            # **target_config 会将字典解包为关键字参数传入
            self.can_bus = can.Bus(**can_channel, timing=timing)

            logger.debug(f"[+] 连接成功！总线状态: {self.can_bus.state}")
        except Exception as e:
            try:
                self.can_bus = can.Bus(**can_channel)
                logger.error(f"[+] {str(e)}，总线状态: {self.can_bus.state}")
            except Exception as e:
                logger.exception(f"[-] 连接失败: {str(e)}")

    def update_can_interface(self):
        if self.bus_connect_state:
            return
        channels = []
        can_interface_name = self.comboBox_NMHardwareType.currentText()
        if can_interface_name in list(CANInterfaceName):
            if can_interface_name == CANInterfaceName.vector:
                for ch in self.can_interface_channels:
                    channels.append(f"{ch['interface']} - {ch['vector_channel_config'].name} - channel {ch['channel']}  {ch['serial']}")

            else:
                if can_interface_name == CANInterfaceName.tosun:
                    for ch in self.can_interface_channels:
                        channels.append(
                            f"{ch['interface']} - {ch['name']} - channel {ch['channel']}  {ch['sn']}")
        self.comboBox_NMHardwareChannel.addItems(channels)

    def update_channels(self, interface_channels):
        try:
            self.comboBox_NMHardwareChannel.clear()
            self.can_interface_channels = interface_channels
            self.update_can_interface()

            if self.can_interface_channels:
                self.current_can_interface = self.can_interface_channels[0]
        except Exception as e:
            logger.exception(f'更新channel失败，{e}')



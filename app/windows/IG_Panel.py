import logging
from typing import Optional, Any

import can
from PySide6.QtCore import Signal, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QWidget, QDialog, QMessageBox
from can import BitTiming, BitTimingFd
from pydantic import BaseModel, field_validator, field_serializer
from enum import Enum

from app.core.db_manager import DBManager
from app.core.interface_manager import CANInterfaceName, InterfaceManager
from app.ui.IGPanelUI import Ui_IG
from app.ui.IgBusConfigPanel_ui import Ui_IgBusConfig

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

    def get_attr_names(self) -> tuple[str, ...]:
        """返回属性名字元组"""
        return tuple(self.model_fields.keys())

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


class CANControllerConfig(BaseModel):
    controller_mode: str = 'CANFD'
    f_clock: int = 80_000_000
    nom_bitrate: int = 500_000
    nom_sample_point: float = 80.0
    data_bitrate: int = 2000_000
    data_sample_point: float = 80.0


class IgBusConfigPanel(Ui_IgBusConfig, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.can_controller_config: CANControllerConfig = CANControllerConfig()

        self.buttonBox.accepted.connect(self._on_accept)

    def _on_accept(self):
        controller_mode = self.comboBox_CANControllerMode.currentText()
        f_clock = self.lineEdit_CANControllerClockFrequency.text()
        nom_bitrate = self.lineEdit_NormalBitrate.text()
        nom_sample_point = self.lineEdit_NormalSamplePoint.text()
        data_bitrate = self.lineEdit_DataBitrate.text()
        data_sample_point = self.lineEdit_DataSamplePoint.text()

        self.can_controller_config.controller_mode = controller_mode
        if not f_clock:
            QMessageBox.warning(self, "输入错误", "时钟频率不能为空！")
            self.lineEdit_CANControllerClockFrequency.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = f_clock.strip()
            try:
                self.can_controller_config.f_clock = int(text)
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "时钟频率输入错误",
                    f"数据格式非法！\n错误原因：{str(e)}\n请输入int类型数据"
                )
                self.lineEdit_CANControllerClockFrequency.setFocus()  # 聚焦到输入框重新输入
                return

        if not nom_bitrate:
            QMessageBox.warning(self, "输入错误", "仲裁段波特率不能为空！")
            self.lineEdit_NormalBitrate.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = nom_bitrate.strip()
            try:
                self.can_controller_config.nom_bitrate = int(text)
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "仲裁段波特率输入错误",
                    f"数据格式非法！\n错误原因：{str(e)}\n请输入int类型数据"
                )
                self.lineEdit_NormalBitrate.setFocus()  # 聚焦到输入框重新输入
                return

        if not nom_sample_point:
            QMessageBox.warning(self, "输入错误", "仲裁段采样点不能为空！")
            self.lineEdit_NormalSamplePoint.setFocus()  # 聚焦到输入框重新输入
            return
        else:
            text = nom_sample_point.strip()
            try:
                self.can_controller_config.nom_sample_point = float(text)
            except Exception as e:
                # 捕获转换异常，提示具体错误
                QMessageBox.critical(
                    self,
                    "仲裁段波特率输入错误",
                    f"数据格式非法！\n错误原因：{str(e)}\n请输入float类型数据"
                )
                self.lineEdit_NormalSamplePoint.setFocus()  # 聚焦到输入框重新输入
                return
        if controller_mode == 'CANFD':
            if not data_bitrate:
                QMessageBox.warning(self, "输入错误", "数据段波特率不能为空！")
                self.lineEdit_DataBitrate.setFocus()  # 聚焦到输入框重新输入
                return
            else:
                text = data_bitrate.strip()
                try:
                    self.can_controller_config.data_bitrate = int(text)
                except Exception as e:
                    # 捕获转换异常，提示具体错误
                    QMessageBox.critical(
                        self,
                        "数据段波特率输入错误",
                        f"数据格式非法！\n错误原因：{str(e)}\n请输入int类型数据"
                    )
                    self.lineEdit_DataBitrate.setFocus()  # 聚焦到输入框重新输入
                    return

            if not data_sample_point:
                QMessageBox.warning(self, "输入错误", "数据段采样点不能为空！")
                self.lineEdit_DataSamplePoint.setFocus()  # 聚焦到输入框重新输入
                return
            else:
                text = data_sample_point.strip()
                try:
                    self.can_controller_config.data_sample_point = float(text)
                except Exception as e:
                    # 捕获转换异常，提示具体错误
                    QMessageBox.critical(
                        self,
                        "数据段采样点输入错误",
                        f"数据格式非法！\n错误原因：{str(e)}\n请输入float类型数据"
                    )
                    self.lineEdit_DataSamplePoint.setFocus()  # 聚焦到输入框重新输入
                    return
        self.accept()


class IgTableModel(QAbstractTableModel):
    def __init__(self, db_manager: DBManager, ig_messages: list[CanIgMessages]):
        super().__init__()
        self.db_manager = db_manager
        self.ig_messages = ig_messages
        self._headers = CanIgMessages().get_attr_names()[:-1]

    def clear(self):
        self.beginResetModel()
        self.ig_messages.clear()
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        """重写表头方法，显示列名"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.ig_messages)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # 显示数据
        if col == 0 and role == Qt.ItemDataRole.CheckStateRole:
            pass
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if role == Qt.ItemDataRole.EditRole:
            pass

        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # 获取默认标志位
        default_flags = super().flags(index)
        flags = default_flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        col = index.column()
        # 检查是否是第 0 列
        if col == 0:
            return flags | Qt.ItemFlag.ItemIsUserCheckable
        elif col == 1:
            return flags
        elif col in (2, 3):
            row = index.row()

        return flags | Qt.ItemFlag.ItemIsEditable


class CANIGPanel(Ui_IG, QWidget):
    signal_scan_can_devices = Signal(str)

    def __init__(self, interface_manager: InterfaceManager, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.can_controller_config: CANControllerConfig = CANControllerConfig()
        self.ig_messages: list[CanIgMessages] = []

        self.can_bus: Optional[can.Bus] = None
        self.current_can_interface = None
        self.can_interface_channels = None
        self.bus_connect_state: bool = False

        self.db_manager = db_manager
        self.interface_manager = interface_manager
        self._ui_init()

        self._signal_init()

    def _ui_init(self):
        self.comboBox_NMHardwareType.addItems(list(CANInterfaceName))

    def _signal_init(self):
        self.pushButton_NMRefreshCANChannel.clicked.connect(self.scan_can_devices)
        self.signal_scan_can_devices.connect(self.interface_manager.can_interface_manager.scan_devices)
        self.interface_manager.can_interface_manager.signal_interface_channels.connect(self.update_channels)
        self.pushButton_NMConnectCANBus.clicked.connect(self.init_can_bus)
        self.pushButton_NMCANbusConfig.clicked.connect(self.open_can_bus_config_panel)

        self.pushButton_NMRefreshCANChannel.clicked.emit()

    def open_can_bus_config_panel(self):
        config_panel = IgBusConfigPanel(self)
        config_panel.setWindowTitle('设置can控制器')
        if config_panel.exec() == QDialog.Accepted:
            pass

    def scan_can_devices(self):
        current_text = self.comboBox_NMHardwareType.currentText()
        self.signal_scan_can_devices.emit(current_text)

    def init_can_bus(self, can_channel):
        try:
            logger.debug(f"[*] 正在连接到 {can_channel['interface']} (通道: {can_channel['channel']}) ...")
            if self.can_controller_config.controller_mode == "CANFD":
                timing = BitTimingFd.from_sample_point(
                    f_clock=self.can_controller_config.f_clock,
                    nom_bitrate=self.can_controller_config.nom_bitrate,
                    nom_sample_point=self.can_controller_config.nom_sample_point,
                    data_bitrate=self.can_controller_config.data_bitrate,
                    data_sample_point=self.can_controller_config.data_sample_point,
                )
            else:
                timing = BitTiming.from_sample_point(
                    f_clock=self.can_controller_config.f_clock,
                    bitrate=self.can_controller_config.nom_bitrate,
                    sample_point=self.can_controller_config.nom_sample_point,
                )

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



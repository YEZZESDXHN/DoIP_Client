import logging
from functools import cached_property
from typing import Optional, Any, List

import can
from PySide6.QtCore import Signal, QAbstractTableModel, Qt, QModelIndex, QEvent, QRect, QTimer, QRegularExpression
from PySide6.QtGui import QIcon, QAction, QCursor, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QDialog, QMessageBox, QStyledItemDelegate, QCheckBox, QStyleOptionButton, QStyle, \
    QApplication, QMenu, QLineEdit, QAbstractItemDelegate, QAbstractItemView, QComboBox
from can import BitTiming, BitTimingFd
from pydantic import BaseModel, field_validator, field_serializer
from enum import Enum, IntEnum

from app.core.db_manager import DBManager
from app.core.interface_manager import CANInterfaceName, InterfaceManager
from app.resources.resources import IconEngine
from app.ui.IGPanelUI import Ui_IG
from app.ui.IgBusConfigPanel_ui import Ui_IgBusConfig
from app.user_data import MessageType, CanIgMessages

logger = logging.getLogger('UDSTool.' + __name__)

CAN_IG_DEFAULT_BIT_TIMING = BitTiming.from_sample_point(f_clock=16_000_000, bitrate=500_000)


CAN_IG_DEFAULT_BIT_TIMING_FD = BitTimingFd.from_sample_point(
    f_clock=80_000_000,
    nom_bitrate=500_000,
    nom_sample_point=80.0,
    data_bitrate=2000_000,
    data_sample_point=80.0,

)


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
        self.comboBox_CANControllerMode.currentIndexChanged.connect(self.on_can_controller_mode_change)

        self.buttonBox.accepted.connect(self._on_accept)

    def on_can_controller_mode_change(self, index):
        if index == 0:
            self.groupBox_data.setVisible(False)
            self.lineEdit_CANControllerClockFrequency.setText('16000000')
        else:
            self.groupBox_data.setVisible(True)
            self.lineEdit_CANControllerClockFrequency.setText('80000000')

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


# 定义步骤的列
class IgTableCol(IntEnum):
    send = 0
    trigger = 1
    name = 2
    id = 3
    type = 4
    data_length = 5
    brs = 6


class IgTableDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        """自定义绘制"""

        if index.column() == IgTableCol.brs:
            # 获取数据
            value = index.data(Qt.ItemDataRole.EditRole)

            # 1. 如果是 Bool 类型，画复选框
            if isinstance(value, bool):
                # 准备绘制参数
                opt = QStyleOptionButton()
                opt.state = QStyle.State_Enabled if (option.state & QStyle.State_Enabled) else QStyle.State_None

                # 设置勾选状态
                if value:
                    opt.state |= QStyle.State_On
                else:
                    opt.state |= QStyle.State_Off

                # --- 计算居中位置 ---
                # 获取当前样式下 CheckBox 的标准尺寸
                checkbox_size = QApplication.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
                # 计算 X, Y 让图标居中
                x = option.rect.x() + (option.rect.width() - checkbox_size) // 2
                y = option.rect.y() + (option.rect.height() - checkbox_size) // 2

                opt.rect.setRect(x, y, checkbox_size, checkbox_size)

                # 绘制复选框 (PE_IndicatorCheckBox 只画框和钩，不画文字)
                QApplication.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorCheckBox, opt, painter)

                # # 如果被选中（高亮），画一个虚线框或者背景色（可选，保持默认即可）
                # if option.state & QStyle.State_Selected:
                #     painter.save()
                #     painter.setPen(option.palette.highlight().color())
                #     painter.setBrush(Qt.BrushStyle.NoBrush)
                #     painter.drawRect(option.rect)  # 简单的选中框
                #     painter.restore()
            else:
                super().paint(painter, option, index)
        elif index.column() == IgTableCol.send:
            value = index.data(Qt.ItemDataRole.EditRole)
            if isinstance(value, bool):
                target_icon = IconEngine.get_icon('stop', 'red') if value else IconEngine.get_icon('start', 'red')

                icon_size = QApplication.style().pixelMetric(QStyle.PixelMetric.PM_ButtonIconSize)
                max_size = min(icon_size, option.rect.height() - 4)

                x = option.rect.x() + (option.rect.width() - icon_size) // 2
                y = option.rect.y() + (option.rect.height() - icon_size) // 2
                target_rect = QRect(x, y, max_size, max_size)

                # mode 参数可以控制图标是 "激活" 还是 "禁用" 状态
                mode = QIcon.Mode.Normal
                if not (option.state & QStyle.State_Enabled):
                    mode = QIcon.Mode.Disabled

                # 开始绘制
                target_icon.paint(painter, target_rect, Qt.AlignmentFlag.AlignCenter, mode)


        # 2. 其他类型，使用默认绘制
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        """处理点击事件，实现单击切换"""

        if index.column() == IgTableCol.brs:
            value = index.data(Qt.ItemDataRole.EditRole)

            # 只拦截 Bool 类型的点击
            if isinstance(value, bool):
                # 判断是否是鼠标左键释放 (Click)
                # 也可以用 MouseButtonPress，但 Release 更符合习惯
                if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                    # 切换数据：True -> False, False -> True
                    new_value = not value
                    # 更新 Model
                    model.setData(index, new_value, Qt.ItemDataRole.EditRole)
                    return True  # 事件已处理，不再向下传递

                # 拦截双击事件，防止双击 bool 列时产生不必要的行为
                if event.type() == QEvent.Type.MouseButtonDblClick:
                    return True
        elif index.column() == IgTableCol.send:
            value = index.data(Qt.ItemDataRole.EditRole)

            # 只拦截 Bool 类型的点击
            if isinstance(value, bool):
                # 判断是否是鼠标左键释放 (Click)
                # 也可以用 MouseButtonPress，但 Release 更符合习惯
                if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                    # 切换数据：True -> False, False -> True
                    new_value = not value
                    # 更新 Model
                    model.setData(index, new_value, Qt.ItemDataRole.EditRole)
                    return True  # 事件已处理，不再向下传递

                # 拦截双击事件，防止双击 bool 列时产生不必要的行为
                if event.type() == QEvent.Type.MouseButtonDblClick:
                    return True

        return super().editorEvent(event, model, option, index)

    def createEditor(self, parent, option, index):
        """禁止 Bool 类型创建默认编辑器"""
        if index.column() == IgTableCol.brs:
            value = index.data(Qt.ItemDataRole.EditRole)
            if isinstance(value, bool):
                return None  # 这一步很关键！防止双击弹出空白框
        elif index.column() == IgTableCol.id:
            editor = QLineEdit(parent)
            regex = QRegularExpression(r"[0-9A-Fa-f]{1,2}")
            validator = QRegularExpressionValidator(regex, editor)
            editor.setValidator(validator)

            # 样式优化：去掉边框，居中显示，让它看起来像是在原地修改
            editor.setFrame(False)
            editor.setAlignment(Qt.AlignmentFlag.AlignCenter)

            editor.textChanged.connect(lambda text: self.check_input(editor, text))

        elif index.column() == IgTableCol.type:
            editor = QComboBox(parent)
            editor.setEditable(True)
            editor.addItems(list(MessageType))
            return editor
        return super().createEditor(parent, option, index)

    def check_input(self, editor: QLineEdit, text: str):
        """检查输入长度"""
        pass
        # if len(text) == 2:
        #     # 1. 提交当前数据 (写入 Model)
        #     self.commitData.emit(editor)


class HexByteDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        try:

            # 1. 限制输入：只能输入 1-2 位 Hex 字符 (0-9, a-f, A-F)
            regex = QRegularExpression(r"[0-9A-Fa-f]{1,2}")
            validator = QRegularExpressionValidator(regex, editor)
            editor.setValidator(validator)

            # 样式优化：去掉边框，居中显示，让它看起来像是在原地修改
            editor.setFrame(False)
            editor.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 2. 自动大写 (可选，提升体验)
            # 也可以在 Validator 里不做限制，这里仅仅是视觉大写

            # 3. 核心功能：监听输入实现自动跳转
            # 当文本改变时调用 self.check_input
            editor.textChanged.connect(lambda text: self.check_input(editor, text))
        except:
            return editor
        return editor

    def setEditorData(self, editor, index):
        """当进入编辑模式时，编辑器显示什么内容"""
        # 获取 Model 中的原始数据 (str)
        value = index.data(Qt.ItemDataRole.EditRole)
        if isinstance(editor, QLineEdit):
            editor.blockSignals(True)
            editor.setText(value)
            editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        """编辑结束，保存数据到 Model"""
        if isinstance(editor, QLineEdit):
            text = editor.text()
            if text:
                # Model 的 setData 已经处理了 Hex 字符串转 int 的逻辑
                # 这里直接传字符串 "FF", "A" 等
                model.setData(index, text, Qt.ItemDataRole.EditRole)

    def check_input(self, editor: QLineEdit, text: str):
        """检查输入长度，如果满2位则自动跳转"""
        if len(text) == 2:
            # 1. 提交当前数据 (写入 Model)
            self.commitData.emit(editor)

            # 2. 关闭当前编辑器，并告诉 View 导航到下一个项目
            # EditNextItem 相当于用户按下了 "Tab" 键
            self.closeEditor.emit(editor, QAbstractItemDelegate.EndEditHint.EditNextItem)


class IgMessageDateTableModel(QAbstractTableModel):
    def __init__(self, db_manager: DBManager, ig_messages: list[CanIgMessages]):
        super().__init__()
        self.db_manager = db_manager
        self.ig_messages = ig_messages
        # 当前需要显示哪一条消息的数据，默认为 -1 (不显示)
        self._current_msg_index = -1
        self._columns = 8  # 固定8列

    def set_current_msg_index(self, index: int):
        """
        切换当前显示的消息索引。
        通常连接到主表格的 selectionModel().currentRowChanged 信号。
        """
        self.beginResetModel()
        if 0 <= index < len(self.ig_messages):
            self._current_msg_index = index
        else:
            self._current_msg_index = -1
        self.endResetModel()

    def _get_current_msg(self) -> Optional[CanIgMessages]:
        if self._current_msg_index != -1:
            return self.ig_messages[self._current_msg_index]
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        msg = self._get_current_msg()
        if not msg:
            return 0

        # 计算行数： (数据长度 + 7) // 8
        # 例如长度为 8 -> 1行
        # 长度为 12 -> 2行
        length = len(msg.data)
        if length == 0:
            return 0
        return (length + self._columns - 1) // self._columns

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._columns

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列头显示 00 01 ... 07
                return f"{section:02X}"
            else:
                # 行头显示偏移量 0x00 0x08 0x10 ...
                return f"0x{section * 8:02X}"
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        msg = self._get_current_msg()
        if not msg:
            return None

        byte_offset = index.row() * self._columns + index.column()

        if byte_offset >= len(msg.data):
            return None

        byte_val = msg.data[byte_offset]

        # --- 修改开始 ---
        # 1. 显示时：返回 "FF" 字符串
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{byte_val:02X}"

        # 2. 编辑时：返回原始 int 数值 (0-255)
        # Delegate 的 setEditorData 会拿到这个 int 并转成 Hex 给用户看
        if role == Qt.ItemDataRole.EditRole:
            return f"{byte_val:02X}"
        # --- 修改结束 ---

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.ToolTipRole:
            return f"Dec: {byte_val}"

        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # 只有在有效数据范围内才允许选中/编辑
        msg = self._get_current_msg()
        if msg:
            byte_offset = index.row() * self._columns + index.column()
            if byte_offset < len(msg.data):
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

        return Qt.ItemFlag.NoItemFlags

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """实现数据编辑，支持输入 Hex 字符串修改 byte"""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        msg = self._get_current_msg()
        if not msg:
            return False

        byte_offset = index.row() * self._columns + index.column()
        if byte_offset >= len(msg.data):
            return False

        try:
            # 假设用户输入的是 Hex 字符串 (如 "FF", "0a")
            new_byte = int(value, 16)

            # 修改 bytes (bytes 是不可变的，需要转 bytearray 或重建)
            # 这里为了简单，转为 mutable 的 bytearray 修改后再转回 bytes
            data_mutable = bytearray(msg.data)
            data_mutable[byte_offset] = new_byte
            msg.data = bytes(data_mutable)
            self.dataChanged.emit(index, index, [role])
            self.db_manager.save_can_ig(msg)
            return True
        except ValueError:
            return False


class IgTableModel(QAbstractTableModel):
    # 参数: (行号)
    sig_length_changed = Signal(int)

    def __init__(self, db_manager: DBManager, ig_messages: list[CanIgMessages], ig_messages_timer: List[QTimer]):
        super().__init__()
        self.db_manager = db_manager
        self.ig_messages = ig_messages
        self.ig_messages_timer = ig_messages_timer
        self._headers = CanIgMessages().get_attr_names()[2:-1]

    def clear(self):
        self.beginResetModel()
        self.ig_messages.clear()
        self.endResetModel()

    def add_message(self, config):
        row = self.rowCount()
        msg = CanIgMessages()
        msg.config = config
        self.beginInsertRows(QModelIndex(), row, row)
        sql_id = self.db_manager.save_can_ig(msg)
        msg.sql_id = sql_id
        self.ig_messages.append(msg)
        self.endInsertRows()



    def delete_message(self, row):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del_num = self.db_manager.delete_can_ig_by_sql_id(self.ig_messages[row].sql_id)
            print(del_num)
            self.ig_messages.pop(row)
            self.ig_messages_timer[row].stop()
            self.ig_messages_timer[row].deleteLater()
            self.ig_messages_timer.pop(row)
            self.endRemoveRows()

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
        msg_tuple = self.ig_messages[row].to_tuple[2:-1]

        # 显示数据
        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == IgTableCol.id:
                return f"{msg_tuple[col]:02X}"
            return msg_tuple[col]
        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        col = index.column()
        field_name = self._headers[col]

        if col == IgTableCol.brs:
            if isinstance(value, bool):
                setattr(self.ig_messages[row], field_name, value)
        elif col == IgTableCol.send:
            if isinstance(value, bool):
                trigger = self.ig_messages[row].trigger
                if trigger == 0:
                    self.ig_messages_timer[row].timeout.emit()
                else:
                    setattr(self.ig_messages[row], field_name, value)
                    if value:
                        self.ig_messages_timer[row].start()
                    else:
                        self.ig_messages_timer[row].stop()
        elif col == IgTableCol.type:
            setattr(self.ig_messages[row], field_name, value)
        elif col == IgTableCol.id:
            msg_id = int(value, 16)
            setattr(self.ig_messages[row], field_name, msg_id)
        elif col == IgTableCol.trigger:
            setattr(self.ig_messages[row], field_name, value)
            self.ig_messages_timer[row].setInterval(value)
            if value == 0:
                self.ig_messages_timer[row].stop()
                setattr(self.ig_messages[row], 'send', False)
        elif col == IgTableCol.data_length:
            msg_type = getattr(self.ig_messages[row], 'type', MessageType.CAN)
            if msg_type in (MessageType.CAN, MessageType.CAN_Remote, MessageType.Extended_CAN, MessageType.Extended_CAN_Remote):
                if value > 8:
                    value = 8
            elif msg_type in (MessageType.CANFD, MessageType.Extended_CANFD):
                if value > 64:
                    value = 64
            else:
                if value > 8:
                    value = 8
            setattr(self.ig_messages[row], field_name, value)

            data = getattr(self.ig_messages[row], 'data', bytes([0] * value))
            if len(data) < value:
                data = data + bytes([0] * (value - len(data)))
            else:
                data = data[:value]
            setattr(self.ig_messages[row], 'data', data)
            self.sig_length_changed.emit(row)
        else:
            setattr(self.ig_messages[row], field_name, value)
        self.db_manager.save_can_ig(self.ig_messages[row])
        return True

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # 获取默认标志位
        default_flags = super().flags(index)
        flags = default_flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        # current_obj = self.ig_messages[index.row()]
        # value = getattr(current_obj, self._headers[index.column()])
        # if isinstance(value, bool):
        #     return flags | Qt.ItemFlag.ItemIsUserCheckable

        return flags | Qt.ItemFlag.ItemIsEditable


class CANIGPanel(Ui_IG, QWidget):
    signal_scan_can_devices = Signal(str)
    signal_config_update = Signal()

    def __init__(self, interface_manager: InterfaceManager, db_manager: DBManager, config, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.can_controller_config: CANControllerConfig = CANControllerConfig()
        self.db_manager = db_manager
        self.config = config
        self.ig_messages: List[CanIgMessages] = self.db_manager.get_can_ig_list_by_config(self.config)
        self.ig_messages_timer: List[QTimer] = []
        self.ig_messages_timer.clear()
        for msg in self.ig_messages:
            msg.send = False
            timer = QTimer()
            timer.setInterval(msg.trigger)
            timer.timeout.connect(self.send_message)
            self.ig_messages_timer.append(timer)

        self.can_bus: Optional[can.Bus] = None
        self.current_can_interface = None
        self.can_interface_channels = None
        self.bus_connect_state: bool = False


        self.interface_manager = interface_manager
        self.messages_model = IgTableModel(db_manager=self.db_manager, ig_messages=self.ig_messages, ig_messages_timer=self.ig_messages_timer)
        self.messages_date_model = IgMessageDateTableModel(db_manager=self.db_manager, ig_messages=self.ig_messages)
        self.tableView_data.setItemDelegate(HexByteDelegate(self.tableView_data))
        self.tableView_data.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.AnyKeyPressed |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self._ui_init()
        self._init_data_context_menu()
        self._signal_init()

    def set_config(self, config):
        self.config = config
        self.signal_config_update.emit()

    def load_ig_messages(self):
        self.ig_messages = self.db_manager.get_can_ig_list_by_config(self.config)
        self.messages_model.beginResetModel()
        self.messages_model.ig_messages = self.ig_messages
        self.messages_model.endResetModel()

    def _init_data_context_menu(self):
        """初始化数据区域右键菜单：复制、清空"""
        # 设置表格视图的上下文菜单策略为自定义（表头的策略已单独设置，不冲突）
        self.tableView_messages.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 绑定数据区域右键菜单信号
        self.tableView_messages.customContextMenuRequested.connect(self._show_data_context_menu)

    def _show_data_context_menu(self, pos):
        """显示数据区域右键菜单"""
        menu = QMenu(self)
        index = self.tableView_messages.indexAt(pos)
        add_action = QAction("add", self)
        add_action.triggered.connect(self.add_message)
        menu.addAction(add_action)

        if index.isValid():
            del_action = QAction("del", self)
            del_action.triggered.connect(lambda: self.delete_message(index.row()))
            menu.addAction(del_action)

        menu.exec(QCursor.pos())
        # menu.exec(self.tableView_messages.mapToGlobal(pos))

    def delete_message(self, row):
        self.messages_model.delete_message(row)

    def add_message(self):
        self.messages_model.add_message(self.config)
        timer = QTimer()
        timer.timeout.connect(self.send_message)
        self.ig_messages_timer.append(timer)

    def _ui_init(self):
        self.comboBox_NMHardwareType.addItems(list(CANInterfaceName))
        self.tableView_messages.setModel(self.messages_model)
        self.tableView_messages.setItemDelegate(IgTableDelegate(self.tableView_messages))

        self.tableView_data.setModel(self.messages_date_model)
        for i in range(8):
            self.tableView_data.setColumnWidth(i, 50)

        self.pushButton_NMConnectCANBus.setIcon(IconEngine.get_icon("unlink", 'red'))

    def _signal_init(self):
        self.pushButton_NMRefreshCANChannel.clicked.connect(self.scan_can_devices)
        self.signal_scan_can_devices.connect(self.interface_manager.can_interface_manager.scan_devices)
        self.interface_manager.can_interface_manager.signal_interface_channels.connect(self.update_channels)
        self.pushButton_NMConnectCANBus.clicked.connect(self.change_bus_connect_state)
        self.pushButton_NMCANbusConfig.clicked.connect(self.open_can_bus_config_panel)

        # 当主表的选择发生变化时，通知数据表切换显示的 Index
        self.tableView_messages.selectionModel().currentRowChanged.connect(self.on_main_row_changed)
        # 监听主表的数据变化
        self.messages_model.sig_length_changed.connect(self.on_data_len_changed)

        self.pushButton_NMRefreshCANChannel.clicked.emit()
        self.signal_config_update.connect(self.load_ig_messages)

    def on_data_len_changed(self, row):
        current_index = self.tableView_messages.currentIndex()
        if not current_index.isValid():
            return

        current_row = current_index.row()

        if current_row == row:
            self.messages_date_model.set_current_msg_index(current_row)

    def on_main_row_changed(self, current_index, previous_index):
        if current_index.isValid():
            # 获取主表当前选中的行号
            row = current_index.row()
            # 通知数据表模型切换观察对象
            self.messages_date_model.set_current_msg_index(row)
        else:
            self.messages_date_model.set_current_msg_index(-1)

    def open_can_bus_config_panel(self):
        config_panel = IgBusConfigPanel(self)
        config_panel.setWindowTitle('设置can控制器')

        config_panel.comboBox_CANControllerMode.setCurrentText(self.can_controller_config.controller_mode)
        config_panel.comboBox_CANControllerMode.currentIndexChanged.emit(
            config_panel.comboBox_CANControllerMode.currentIndex())
        config_panel.lineEdit_DataBitrate.setText(str(self.can_controller_config.data_bitrate))
        config_panel.lineEdit_NormalBitrate.setText(str(self.can_controller_config.nom_bitrate))
        config_panel.lineEdit_CANControllerClockFrequency.setText(str(self.can_controller_config.f_clock))
        config_panel.lineEdit_DataSamplePoint.setText(str(self.can_controller_config.data_sample_point))
        config_panel.lineEdit_NormalSamplePoint.setText(str(self.can_controller_config.nom_sample_point))
        
        if config_panel.exec() == QDialog.Accepted:
            self.can_controller_config = config_panel.can_controller_config

    def scan_can_devices(self):
        current_text = self.comboBox_NMHardwareType.currentText()
        self.signal_scan_can_devices.emit(current_text)

    def change_ui_state_disabled(self, state: bool):
        self.comboBox_NMHardwareType.setDisabled(state)
        self.comboBox_NMHardwareChannel.setDisabled(state)
        self.pushButton_NMRefreshCANChannel.setDisabled(state)
        self.pushButton_NMCANbusConfig.setDisabled(state)

    def change_bus_connect_state(self):
        if self.bus_connect_state:
            self.can_bus.shutdown()
            self.bus_connect_state = False
            self.pushButton_NMConnectCANBus.setIcon(IconEngine.get_icon("unlink", 'red'))
            self.change_ui_state_disabled(False)
        else:
            self.init_can_bus()

    def init_can_bus(self):
        try:
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
            self.can_bus = can.Bus(**self.current_can_interface, timing=timing)
            self.bus_connect_state = True
            self.pushButton_NMConnectCANBus.setIcon(IconEngine.get_icon("link", 'green'))
            self.change_ui_state_disabled(True)
            logger.debug(f"[+] 连接成功！总线状态: {self.can_bus.state}")
        except Exception as e:
            try:
                self.can_bus = can.Bus(**self.current_can_interface)
                self.bus_connect_state = True
                self.pushButton_NMConnectCANBus.setIcon(IconEngine.get_icon("link", 'green'))
                self.change_ui_state_disabled(True)
            except Exception as e:
                self.bus_connect_state = False
                self.pushButton_NMConnectCANBus.setIcon(IconEngine.get_icon("unlink", 'red'))
                logger.exception(f"[-] 连接失败: {str(e)}")

    def update_can_interface(self, interface_channels):
        if self.bus_connect_state:
            return
        self.comboBox_NMHardwareChannel.clear()
        self.can_interface_channels = interface_channels
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
            self.update_can_interface(interface_channels)

            if self.can_interface_channels:
                self.current_can_interface = self.can_interface_channels[0]
        except Exception as e:
            logger.exception(f'更新channel失败，{e}')

    def send_message(self):
        if not self.bus_connect_state:
            return
        timer = self.sender()

        # 2. 在列表中查找它的索引
        if timer in self.ig_messages_timer:
            index = self.ig_messages_timer.index(timer)

            '''
            timestamp: float = 0.0,
            arbitration_id: int = 0,
            is_extended_id: bool = True,
            is_remote_frame: bool = False,
            is_error_frame: bool = False,
            channel: Optional[typechecking.Channel] = None,
            dlc: Optional[int] = None,
            data: Optional[typechecking.CanData] = None,
            is_fd: bool = False,
            is_rx: bool = True,
            bitrate_switch: bool = False,
            error_state_indicator: bool = False,
            check: bool = False,
            '''
            ig_messages = self.ig_messages[index]

            if ig_messages.type == MessageType.CAN:
                is_fd = False
                is_extended_id = False
                is_remote_frame = False
            elif ig_messages.type == MessageType.CAN_Remote:
                is_fd = False
                is_extended_id = False
                is_remote_frame = True
            elif ig_messages.type == MessageType.CANFD:
                is_fd = True
                is_extended_id = False
                is_remote_frame = False
            elif ig_messages.type == MessageType.Extended_CAN:
                is_fd = False
                is_extended_id = True
                is_remote_frame = False
            elif ig_messages.type == MessageType.Extended_CAN_Remote:
                is_fd = False
                is_extended_id = True
                is_remote_frame = True
            elif ig_messages.type == MessageType.Extended_CANFD:
                is_fd = True
                is_extended_id = True
                is_remote_frame = False
            else:
                is_fd = False
                is_extended_id = False
                is_remote_frame = False
            msg = can.Message(
                arbitration_id=ig_messages.id,
                data=ig_messages.data,
                is_extended_id=is_extended_id,
                is_fd=is_fd,
                is_remote_frame=is_remote_frame,
                dlc=ig_messages.data_length,
                check=True  # 检查数据长度等参数是否合法
            )
            self.can_bus.send(msg)



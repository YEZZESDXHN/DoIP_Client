import ipaddress
import logging

from PySide6.QtCore import Signal, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QTableView, QVBoxLayout, QScrollBar

from DoIPConfigUI import Ui_Dialog
from utils import hex_str_to_int

logger = logging.getLogger("UDSOnIPClient")


class DoIPConfigPanel(QDialog, Ui_Dialog):
    """
    配置面板类，继承自 QDialog (窗口行为) 和 Ui_Dialog (界面布局)
    """

    config_signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.send_config_signal)

    @Slot()
    def send_config_signal(self):
        try:
            if self.lineEdit_TesterLogicalAddress.text():
                tester_logical_address = hex_str_to_int(self.lineEdit_TesterLogicalAddress.text())
            else:
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    'tester logical address 输入为空',  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error('tester logical address 输入为空')
                return
        except Exception as e:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                str(e),  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.exception(e)
            return

        try:
            if self.lineEdit_TesterLogicalAddress.text():
                DUT_logical_address = hex_str_to_int(self.lineEdit_DUTLogicalAddress.text())
            else:
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    'DUT logical address 输入为空',  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error('DUT logical address 输入为空')
                return
        except Exception as e:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                str(e),  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.exception(e)
            return

        if self.lineEdit_DUT_IP.text():
            DUT_ip_raw_str = self.lineEdit_DUT_IP.text()
            ip_object = ipaddress.ip_address(DUT_ip_raw_str)
            if ip_object.version == 4:
                DUT_ipv4_address = DUT_ip_raw_str
            else:
                error_message = f'DUT IPv4输入错误:{DUT_ip_raw_str}'
                QMessageBox.critical(
                    self,  # 父窗口设置为 self (MainWindow)
                    "Error",  # 标题
                    error_message,  # 内容
                    QMessageBox.StandardButton.Ok
                )
                logger.error(error_message)
                return
        else:
            QMessageBox.critical(
                self,  # 父窗口设置为 self (MainWindow)
                "Error",  # 标题
                'DUT IP 输入为空',  # 内容
                QMessageBox.StandardButton.Ok
            )
            logger.error('DUT IP 输入为空')
            return
        config = {'tester_logical_address': tester_logical_address,
                  'DUT_logical_address': DUT_logical_address,
                  'DUT_ipv4_address': DUT_ipv4_address}
        self.config_signal.emit(config)
        self.accept()



class DoIPTraceTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.max_rows = 500
        self._data = []
        self._headers = ["时间戳", "方向", "类型", "源地址", "目标地址", "Data"]

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None  # PySide6直接返回None

        row = index.row()
        col = index.column()

        # 1. 显示数据
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[row][col]

        # # 2. 单元格背景色（规范写法：返回QColor对象）
        # elif role == Qt.ItemDataRole.BackgroundRole:
        #     status = self._data[row][7]
        #     direction = self._data[row][2]
        #
        #     if status == "失败":
        #         return QColor(Qt.GlobalColor.red)  # 显式引用GlobalColor枚举
        #     elif direction == "Tx":
        #         return QColor(Qt.GlobalColor.blue)
        #     elif direction == "Rx":
        #         return QColor(Qt.GlobalColor.green)

        # 其他角色返回None
        return None

    # 用于追加 Trace 数据
    def append_trace_data(self, trace_row):
        """
        向模型中添加一行 DoIP Trace 数据
        :param trace_row: 列表，长度需与列数一致
        """
        if len(trace_row) != len(self._headers):
            raise ValueError(f"数据长度必须为 {len(self._headers)}，当前为 {len(trace_row)}")

        # 计算需要删除的旧行数量
        excess_rows = len(self._data) - self.max_rows
        if excess_rows > 0:
            # 1. 通知视图：要删除从0到excess_rows-1的行（批量删除）
            self.beginRemoveRows(QModelIndex(), 0, excess_rows - 1)
            # 2. 批量删除：保留最后max_rows行（切片直接截取，效率最高）
            self._data = self._data[excess_rows:]
            # 3. 通知视图：删除完成
            self.endRemoveRows()

        # 通知 Qt 模型：开始插入行（必须调用，否则视图不刷新）
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(trace_row)
        # 通知 Qt 模型：插入行完成
        self.endInsertRows()

    # 重写表头方法，让 QTableView 显示列名
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None


class DoIPTraceTableView(QTableView):
    """DoIP追踪表格，直接继承QTableView"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自动滚动开关：默认开启
        self._auto_scroll = True
        # 初始化表格模型
        self.trace_model = DoIPTraceTableModel()
        # 初始化表格属性
        self._init_ui()
        # 绑定滚动条监听
        self._bind_scroll_listener()

    def _init_ui(self):
        """初始化表格的UI属性"""
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setModel(self.trace_model)  # 设置模型

    def _bind_scroll_listener(self):
        """绑定滚动条的信号，监听滚动状态"""
        scroll_bar: QScrollBar = self.verticalScrollBar()
        scroll_bar.valueChanged.connect(self._on_scroll_value_changed)

    @Slot(int)
    def _on_scroll_value_changed(self, value: int):
        """根据滚动条位置更新自动滚动状态"""
        scroll_bar = self.verticalScrollBar()
        max_value = scroll_bar.maximum()
        self._auto_scroll = (value == max_value)
        if self._auto_scroll:
            logger.debug("表格滚动到最底部，开启自动滚动")
        else:
            logger.debug("用户滚动到旧数据，关闭自动滚动")

    def _scroll_to_bottom(self):
        """强制滚动到表格底部"""
        self.scrollToBottom()

    def add_trace_data(self, data: list):
        """对外暴露的接口：添加追踪数据到表格"""
        self.trace_model.append_trace_data(data)
        # 若开启自动滚动，滚动到底部
        if self._auto_scroll:
            self._scroll_to_bottom()

    def clear_trace_data(self):
        """对外暴露的接口：清空表格数据"""
        self.trace_model.clear()  # 需确保模型有clear方法

    @property
    def auto_scroll(self) -> bool:
        """获取自动滚动状态"""
        return self._auto_scroll

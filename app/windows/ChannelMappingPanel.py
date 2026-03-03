import sys
from typing import Any

from PySide6.QtCore import Signal, QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QDialog, QApplication, QStyledItemDelegate, QComboBox, QLineEdit

from app.core.db_manager import DBManager
from app.core.interface_manager import InterfaceManager
from app.resources.resources import IconEngine
from app.ui.ChannelMapping import Ui_Dialog_ChannelMapping


class ChannelMappingPanel(Ui_Dialog_ChannelMapping, QDialog):

    def __init__(self, interface_manager: InterfaceManager, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.interface_manager = interface_manager
        self.db_manager = db_manager
        self.eth_interfaces = []
        self.can_interfaces = {}

        eth_channel_table_model_data = []
        for bus_name, channel in self.interface_manager.channel_mappings.eth.mappings.items():
            eth_channel_table_model_data.append([bus_name, channel])
        self.eth_channel_table_model = EthChannelTableModel(eth_channel_table_model_data)
        # self.eth_channel_table_model.update_row_count(len(self.interface_manager.channel_mappings.eth.mappings))
        self.eth_channel_table_delegate = EthChannelTableDelegate(self.eth_interfaces, self.eth_channel_table_model)

        can_channel_table_model_data = []
        for bus_name, channel in self.interface_manager.channel_mappings.can.mappings.items():
            can_channel_table_model_data.append([bus_name, channel.channel])
        self.can_channel_table_model = CanChannelTableModel(can_channel_table_model_data)
        # self.can_channel_table_model.update_row_count(len(self.interface_manager.channel_mappings.can.mappings))
        self.can_channel_table_delegate = CanChannelTableDelegate(self.can_interfaces, self.can_channel_table_model)

        self.init_ui()
        self.init_signal()
        self.pushButton_Refresh.clicked.emit()

    def init_signal(self):
        self.pushButton_Refresh.clicked.connect(self.interface_manager.scan_interfaces)
        self.interface_manager.signal_can_interface_channels.connect(self.update_can_interfaces)
        self.interface_manager.signal_eth_interface_channels.connect(self.update_eth_interfaces)
        self.comboBox_CanNum.currentIndexChanged.connect(self.can_channel_table_model.update_row_count)
        self.comboBox_EthNum.currentIndexChanged.connect(self.eth_channel_table_model.update_row_count)

    def init_ui(self):
        self.setWindowTitle("ChannelMapping")
        self.setWindowIcon(IconEngine.get_icon('config'))
        self.pushButton_Refresh.setIcon(IconEngine.get_icon("refresh"))
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        self.tableView_CanChannels.setModel(self.can_channel_table_model)
        self.tableView_CanChannels.setItemDelegate(self.can_channel_table_delegate)
        self.tableView_EthChannels.setModel(self.eth_channel_table_model)
        self.tableView_EthChannels.setItemDelegate(self.eth_channel_table_delegate)

    def update_can_interfaces(self, interfaces):
        current_index = self.can_channel_table_model.row_count

        self.can_interfaces = interfaces
        self.can_channel_table_delegate.update_can_interfaces(self.can_interfaces)
        self.comboBox_CanNum.blockSignals(True)
        self.comboBox_CanNum.clear()
        max_num = len(self.can_interfaces)
        num_list = [str(i) for i in range(max_num + 1)]
        self.comboBox_CanNum.addItems(num_list)
        self.comboBox_CanNum.blockSignals(False)
        if max_num >= current_index + 1:
            self.comboBox_CanNum.setCurrentIndex(current_index)
        else:
            self.comboBox_CanNum.setCurrentIndex(max_num - 1)
        # print(self.can_interfaces)

    def update_eth_interfaces(self, interfaces):
        self.eth_interfaces = interfaces
        current_index = self.eth_channel_table_model.row_count
        self.eth_channel_table_delegate.update_eth_interfaces(self.eth_interfaces)
        self.comboBox_EthNum.blockSignals(True)
        self.comboBox_EthNum.clear()
        max_num = len(self.eth_interfaces)
        num_list = [str(i) for i in range(max_num + 1)]
        self.comboBox_EthNum.addItems(num_list)
        self.comboBox_EthNum.blockSignals(False)
        if max_num >= current_index + 1:
            self.comboBox_EthNum.setCurrentIndex(current_index)
        else:
            self.comboBox_EthNum.setCurrentIndex(max_num - 1)
        # print(self.eth_interfaces)


class EthChannelTableDelegate(QStyledItemDelegate):
    def __init__(self, eth_interfaces, parent=None):
        super().__init__(parent)
        self.eth_interfaces = eth_interfaces
        self.eth_interfaces_display = list(self.eth_interfaces)

    def update_eth_interfaces(self, eth_interfaces):
        """更新Eth接口数据源"""
        self.eth_interfaces = eth_interfaces
        self.eth_interfaces_display = list(self.eth_interfaces)

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            editor = QComboBox(parent)
            # editor.setEditable(True)

            editor.addItems(self.eth_interfaces_display)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value and isinstance(editor, QComboBox):
            editor.setCurrentText(str(value))
        elif value and isinstance(editor, QLineEdit):
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.currentText()
            model.setData(index, value, Qt.EditRole)
        elif isinstance(editor, QLineEdit):
            value = editor.text()
            model.setData(index, value, Qt.EditRole)


class EthChannelTableModel(QAbstractTableModel):
    def __init__(self, data: list, parent=None):
        super().__init__(parent)
        # 存储表格数据：二维列表 [(自定义CAN名称, 接口1), (自定义CAN名称, 接口2), ...]
        self.table_data = data
        self.row_count = len(self.table_data)
        # self.table_data.append(["Eth 1", ""])

    def update_row_count(self, new_row_count):
        """更新表格行数"""
        if new_row_count < 0:
            new_row_count = 0

        # 开始模型数据变更
        self.beginResetModel()

        # 行数增加：仅对新增的行填充默认 "CAN+行号"
        if new_row_count > self.row_count:
            for i in range(self.row_count, new_row_count):
                # 新增行的行号是 i+1
                default_can_name = f"Eth {i + 1}"
                self.table_data.append([default_can_name, ""])
        # 行数减少：删除多余行
        elif new_row_count < self.row_count:
            self.table_data = self.table_data[:new_row_count]

        # 更新行数并结束变更
        self.row_count = new_row_count
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return 2

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """重写：设置表头"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Eth", "Channel"][section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        """重写：返回单元格数据（第一列保留用户编辑后的值）"""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # 显示/编辑角色：返回单元格实际存储的内容
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if row < len(self.table_data):
                return self.table_data[row][col]

        return None

    def setData(self, index, value, role=Qt.EditRole):
        """设置单元格数据"""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        # 确保行索引有效
        if row < len(self.table_data):
            # 直接更新存储的数值（第一列修改后永久保留）
            self.table_data[row][col] = value
            # 通知视图数据已更新
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """重写：设置单元格可编辑（第一列完全可编辑）"""
        if not index.isValid():
            return Qt.NoItemFlags
        # 所有单元格都可编辑、选择、启用
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class CanChannelTableDelegate(QStyledItemDelegate):
    def __init__(self, can_interfaces, parent=None):
        super().__init__(parent)
        self.can_interfaces = can_interfaces
        self.can_interfaces_display = list(self.can_interfaces)

    def update_can_interfaces(self, can_interfaces):
        """更新CAN接口数据源"""
        self.can_interfaces = can_interfaces
        self.can_interfaces_display = list(self.can_interfaces)

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            editor = QComboBox(parent)
            # editor.setEditable(True)
            editor.addItems(self.can_interfaces_display)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value and isinstance(editor, QComboBox):
            editor.setCurrentText(str(value))
        elif value and isinstance(editor, QLineEdit):
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.currentText()
            model.setData(index, value, Qt.EditRole)
        elif isinstance(editor, QLineEdit):
            value = editor.text()
            model.setData(index, value, Qt.EditRole)


class CanChannelTableModel(QAbstractTableModel):
    """CAN通道表格模型（调整后：仅新增行时填充默认CAN名称）"""

    def __init__(self, data: list, parent=None):
        super().__init__(parent)
        self.table_data = data
        self.row_count = len(self.table_data)
        # self.table_data.append(["CAN 1", ""])

    # def update_can_interfaces(self, can_interfaces):
    #     """更新CAN接口数据源"""
    #     self.can_interfaces = can_interfaces
    #     # 通知视图数据已更改
    #     self.dataChanged.emit(self.index(0, 1), self.index(self.row_count - 1, 1))

    def update_row_count(self, new_row_count):
        """更新表格行数"""
        if new_row_count < 0:
            new_row_count = 0

        # 开始模型数据变更
        self.beginResetModel()

        # 行数增加：仅对新增的行填充默认 "CAN+行号"
        if new_row_count > self.row_count:
            for i in range(self.row_count, new_row_count):
                # 新增行的行号是 i+1
                default_can_name = f"CAN {i + 1}"
                self.table_data.append([default_can_name, ""])
        # 行数减少：删除多余行
        elif new_row_count < self.row_count:
            self.table_data = self.table_data[:new_row_count]

        # 更新行数并结束变更
        self.row_count = new_row_count
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return 2

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """重写：设置表头"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["CAN", "Channel"][section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        """重写：返回单元格数据（第一列保留用户编辑后的值）"""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # 显示/编辑角色：返回单元格实际存储的内容
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if row < len(self.table_data):
                return self.table_data[row][col]

        return None

    def setData(self, index, value, role=Qt.EditRole):
        """设置单元格数据"""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        # 确保行索引有效
        if row < len(self.table_data):
            # 直接更新存储的数值（第一列修改后永久保留）
            self.table_data[row][col] = value
            # 通知视图数据已更新
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """重写：设置单元格可编辑（第一列完全可编辑）"""
        if not index.isValid():
            return Qt.NoItemFlags
        # 所有单元格都可编辑、选择、启用
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = ChannelMappingPanel()
    panel.show()
    sys.exit(app.exec())
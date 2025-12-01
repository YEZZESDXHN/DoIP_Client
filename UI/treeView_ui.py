import logging

from PySide6.QtCore import QModelIndex, Signal, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QTreeView, QMenu, QMessageBox, QDialog, QHeaderView

from UI.AddDiagServiceDialog import Ui_AddDiagServiceDialog
from utils import hex_str_to_bytes

logger = logging.getLogger("UiCustom")

DEFAULT_SERVICES_TREE = {
            'DiagnosticSessionControl (0x10)': {
                'defaultSession (01)': bytes.fromhex('1001'),
                'programmingSession (02)': bytes.fromhex('1002'),
                'extendedDiagnosticSession (03)': bytes.fromhex('1003'),
                'safetySystemDiagnosticSession (04)': bytes.fromhex('1004'),
            },
            'ECUReset (0x11)': {
                'hardReset (01)': bytes.fromhex('1101'),
                'keyOffOnReset (02)': bytes.fromhex('1102'),
                'softReset (03)': bytes.fromhex('1103'),
                'enableRapidPowerShutDown (04)': bytes.fromhex('1104'),
                'disableRapidPowerShutDown (05)': bytes.fromhex('1105'),
            },
            'ReadDataByIdentifier (0x22)': {

            },
            'InputOutputControlByIdentifier (0x2F)': {

            },
            'ReadDTCInformation (0x19)': {

            },
            'RequestDownload (0x34)': {

            },
            'RequestUpload (0x35)': {

            },
            'TransferData (0x36)': {

            },
            'RequestTransferExit (0x37)': {

            },
            'SecurityAccess (0x27)': {
                'RequestSeed L1': bytes.fromhex('2701'),
                'RequestSeed L3': bytes.fromhex('2703'),
                'RequestSeed L5': bytes.fromhex('2705'),
            },
            'TesterPresent (0x3E)': {

            },
            'RoutineControl (0x31)': {
                'startRoutine (01)': {},
                'stopRoutine (02)': {},
                'requestRoutineResults (03)': {},
            }

        }

# ------------------------------
# 树形数据模型：存储bytes类型的自定义数据
# ------------------------------
class DiagTreeDataModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["诊断服务"])
        self.services_tree = DEFAULT_SERVICES_TREE
        self._init_default_nodes()


    def _init_default_nodes(self):
        """初始化默认节点（存储bytes类型数据）"""
        invisible_root = self.invisibleRootItem()

        for _service, _sub_services in self.services_tree.items():
            _service_item = QStandardItem(_service)
            invisible_root.appendRow(_service_item)

            for _sub_service, _sub_service_data in _sub_services.items():

                if isinstance(_sub_service_data, bytes):
                    _sub_service_item = QStandardItem(_sub_service)
                    _sub_service_item.setData(_sub_service_data, Qt.ItemDataRole.UserRole)
                    _service_item.appendRow(_sub_service_item)
                if isinstance(_sub_service_data, dict):
                    for _name, _data in _sub_service_data.items():
                        _item = QStandardItem(_name)
                        _item.setData(_data, Qt.ItemDataRole.UserRole)
                        _service_item.appendRow(_item)


    def add_child_node(self, parent_index: QModelIndex, node_name: str, custom_bytes: bytes = b""):
        """添加子节点（接收bytes类型数据）"""
        if not parent_index.isValid() or not node_name.strip():
            return False
        parent_item = self.itemFromIndex(parent_index)
        new_item = QStandardItem(node_name.strip())
        new_item.setData(custom_bytes, Qt.ItemDataRole.UserRole)  # 存储bytes
        parent_item.appendRow(new_item)
        return True

    def add_root_node(self, node_name: str, custom_bytes: bytes = b""):
        """添加顶级根节点（接收bytes类型数据）"""
        if not node_name.strip():
            return False
        invisible_root = self.invisibleRootItem()
        new_root = QStandardItem(node_name.strip())
        # new_root.setData(custom_bytes, Qt.ItemDataRole.UserRole)
        invisible_root.appendRow(new_root)
        return True

    def delete_node(self, node_index: QModelIndex):
        """删除节点"""
        if not node_index.isValid():
            return False
        parent_item = self.itemFromIndex(node_index.parent())
        row = node_index.row()
        if not parent_item:
            parent_item = self.invisibleRootItem()
        parent_item.removeRow(row)
        return True

    def get_node_info(self, node_index: QModelIndex) -> dict:
        """获取节点信息（bytes转Hex字符串展示）"""
        if not node_index.isValid():
            return {}
        node_text = node_index.data(Qt.ItemDataRole.DisplayRole)
        custom_bytes = node_index.data(Qt.ItemDataRole.UserRole)  # 获取bytes数据
        # 计算节点层级
        node_level = 0
        temp_index = node_index
        while temp_index.parent().isValid():
            node_level += 1
            temp_index = temp_index.parent()
        # bytes转Hex字符串（大写），空bytes显示"无"
        hex_str = custom_bytes.hex().upper() if custom_bytes else "无"
        return {
            "text": node_text,
            "hex_str": hex_str,       # 格式化后的Hex字符串
            "raw_bytes": custom_bytes,# 原始bytes数据
            "level": node_level
        }



# ------------------------------
# 自定义树形视图：处理bytes数据的交互
# ------------------------------
class DiagTreeView(QTreeView):

    clicked_node_data = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_view()
        self._init_context_menu()

    def _init_view(self):
        """初始化视图配置"""
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)  # 单选
        self.setIndentation(20)  # 缩进距离
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 开启右键菜单

        # 绑定信号
        # self.clicked.connect(self._on_node_clicked)
        self.doubleClicked.connect(self._on_sub_service_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _init_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        self.add_root_act = self.context_menu.addAction("添加服务")
        self.add_child_act = self.context_menu.addAction("添加子服务")
        self.context_menu.addSeparator()
        self.delete_act = self.context_menu.addAction("删除(子)服务")
        self.add_child_act.triggered.connect(self._add_child_node)
        self.add_root_act.triggered.connect(self._add_root_node)
        self.delete_act.triggered.connect(self._delete_node)

    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单"""
        global_pos = self.mapToGlobal(pos)
        self.context_menu.exec(global_pos)

    def _on_sub_service_double_clicked(self, index: QModelIndex):
        """双击服务，为一级节点时获取节点数据并发送"""
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            return
        node_info = model.get_node_info(index)
        if not node_info:
            return
        if node_info['level'] == 1:
            self.clicked_node_data.emit(node_info.get('raw_bytes', bytes()))


    def _on_node_clicked(self, index: QModelIndex):
        """节点点击：展示Hex字符串和字节长度"""
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            return
        node_info = model.get_node_info(index)
        if not node_info:
            return
        # 组装展示信息：Hex字符串 + 字节长度
        display_text = (
            f"节点文本：{node_info['text']}\n"
            f"Hex数据：{node_info['hex_str']}\n"
            # f"字节长度：{len(node_info['raw_bytes'])}\n"
            f"节点层级：{node_info['level']}"
        )
        QMessageBox.information(self, "节点信息", display_text)

    def _add_child_node(self):
        """添加子节点：调用对话框获取bytes数据"""
        current_index = self.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "提示", "请先选中一个节点再添加子节点！")
            return

        dialog = AddNodeDialog(self, title="添加子服务")
        if dialog.exec() == QDialog.Accepted:
            node_name, custom_bytes = dialog.get_inputs()
            model = self.model()
            if isinstance(model, DiagTreeDataModel):
                success = model.add_child_node(current_index, node_name, custom_bytes)
                if success:
                    self.expand(current_index)

    def _add_root_node(self):
        """添加顶级根节点：调用对话框获取bytes数据"""
        dialog = AddNodeDialog(self, title="添加服务")
        dialog.lineEdit_Hex.setVisible(False)
        dialog.label_Hex.setVisible(False)
        dialog.label_note.setVisible(False)
        if dialog.exec() == QDialog.Accepted:
            node_name, custom_bytes = dialog.get_inputs()
            model = self.model()
            if isinstance(model, DiagTreeDataModel):
                model.add_root_node(node_name, custom_bytes)

    def _delete_node(self):
        """删除节点"""
        current_index = self.currentIndex()
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            QMessageBox.warning(self, "提示", "数据模型异常！")
            return
        success = model.delete_node(current_index)
        if not success:
            QMessageBox.warning(self, "提示", "删除节点失败，请选中有效节点！")

class AddNodeDialog(Ui_AddDiagServiceDialog, QDialog):
    def __init__(self, parent=None, title="添加节点"):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.node_name = ""
        self.custom_bytes = b""  # 存储转换后的bytes数据

        self.buttonBox.accepted.connect(self._on_accept)

    def _on_accept(self):
        """点击确认按钮：校验名称 + Hex转bytes（捕获异常）"""
        # 1. 校验节点名称
        self.node_name = self.lineEdit_name.text().strip()
        if not self.node_name:
            QMessageBox.warning(self, "输入错误", "节点名称不能为空！")
            self.lineEdit_name.setFocus()  # 聚焦到输入框重新输入
            return

        # 2. Hex字符串转bytes（捕获异常）
        hex_input = self.lineEdit_Hex.text().strip()
        try:
            self.custom_bytes = hex_str_to_bytes(hex_input)
        except ValueError as e:
            # 捕获转换异常，提示具体错误
            QMessageBox.critical(
                self,
                "Hex转换失败",
                f"数据格式非法！\n错误原因：{str(e)}\n请输入合法的十六进制字符串（如1A3F、FF00）。"
            )
            self.lineEdit_Hex.setFocus()  # 聚焦到输入框重新输入
            return

        # 3. 校验通过，关闭对话框
        self.accept()

    def get_inputs(self):
        """获取用户输入结果：(节点名称, 转换后的bytes数据)"""
        return self.node_name, self.custom_bytes

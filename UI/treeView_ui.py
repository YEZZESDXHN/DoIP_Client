import dataclasses
import json
import logging
import re
from typing import List, Type, Optional, get_args

from PySide6.QtCore import QModelIndex, Signal, QPoint, QMimeData, QByteArray, QDataStream, QIODevice
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QDrag
from PySide6.QtWidgets import QTreeView, QMenu, QMessageBox, QDialog, QHeaderView

from UI.AddDiagServiceDialog import Ui_AddDiagServiceDialog
from user_data import DiagnosisStepData, DiagnosisStepTypeEnum, UdsService, DEFAULT_SERVICES
from utils import hex_str_to_bytes, json_default_converter

logger = logging.getLogger("UiCustom")


# ------------------------------
# 树形数据模型：存储bytes类型的自定义数据
# ------------------------------
class DiagTreeDataModel(QStandardItemModel):
    def __init__(self, uds_service: UdsService, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["诊断服务"])
        self.uds_service = uds_service
        uds_service_dict = uds_service.to_dict()

        self.payload_role = Qt.ItemDataRole.UserRole
        self.path_role = Qt.ItemDataRole.UserRole + 1
        self.node_type_role = Qt.ItemDataRole.UserRole + 2

        invisible_root = self.invisibleRootItem()
        self._init_nodes(invisible_root, uds_service_dict)

    def _init_nodes(self, parent_node, data: dict, current_path=''):
        """
        递归地将字典或列表数据添加到 QStandardItem 树结构中。

        """
        if isinstance(data, dict):
            # 遍历字典的键值对
            for key, value in data.items():
                # 创建一个新节点作为当前节点的子节点
                new_path = key if not current_path else f"{current_path}.{key}"
                node = QStandardItem(str(key))
                node.setData(new_path, self.path_role)
                if isinstance(value, list):
                    node.setData(0, self.node_type_role)
                else:
                    node.setData(-1, self.node_type_role)
                parent_node.appendRow(node)

                # 递归调用自身处理值 (value)
                self._init_nodes(node, value, new_path)

        elif isinstance(data, list):
            # 遍历列表中的每个项目 (item)
            for index, item in enumerate(data):
                if isinstance(item, dict) and 'name' in item and 'payload' in item:
                    path = f"{current_path}[{index}]"
                    # 假设列表项是带有 'name' 和 'payload' 的结构
                    node = QStandardItem(item['name'])
                    # 设置用户数据
                    node.setData(item['payload'], self.path_role)
                    node.setData(path, self.path_role)
                    node.setData(1, self.node_type_role)
                    parent_node.appendRow(node)

    def add_operation_node(self, parent_index: QModelIndex, node_name: str, custom_bytes: bytes = b""):
        """添加operation_node（接收bytes类型数据）"""
        if not parent_index.isValid() or not node_name.strip():
            return False
        parent_item = self.itemFromIndex(parent_index)
        parent_path = self.get_node_path(parent_index)
        obj = self.get_obj_from_path(parent_path)

        new_item = QStandardItem(node_name.strip())
        new_item.setData(custom_bytes, self.payload_role)  # 存储bytes
        new_item.setData(1, self.node_type_role)  # 终端节点
        path = f"{parent_path}[{len(obj)}]"
        new_item.setData(path, self.path_role)
        parent_item.appendRow(new_item)
        data_type: Type = self.get_parent_node_data_type(parent_index)
        if isinstance(obj, list):
            obj.append(data_type(name=node_name, payload=custom_bytes))

        return True

    # def add_root_node(self, node_name: str):
    #     """添加顶级根节点（接收bytes类型数据）"""
    #     if not node_name.strip():
    #         return False
    #     invisible_root = self.invisibleRootItem()
    #     new_root = QStandardItem(node_name.strip())
    #     # new_root.setData(custom_bytes, Qt.ItemDataRole.UserRole)
    #     invisible_root.appendRow(new_root)
    #     return True

    def delete_operation_node(self, node_index: QModelIndex):
        """删除终端节点节点"""
        if not node_index.isValid():
            return False
        if self.get_node_type(node_index) != 1:
            return False
        node_path = self.get_node_path(node_index)
        parts: List[str] = self.split_path_to_parts(node_path)
        parent_item = self.itemFromIndex(node_index.parent())
        row = node_index.row()
        if not parent_item:
            parent_item = self.invisibleRootItem()
        parent_item.removeRow(row)
        obj = self.uds_service
        for part in parts[:-1]:
            if not isinstance(obj, list):
                obj = getattr(obj, part)
            else:
                obj = obj[int(part)]
        if isinstance(obj, list):
            obj.pop(int(parts[-1]))

        return True

    def get_node_path(self, node_index: QModelIndex):
        """获取节点信息（bytes转Hex字符串展示）"""
        if not node_index.isValid():
            return {}
        return node_index.data(self.path_role)

    def get_parent_node_data_type(self, node_index: QModelIndex) -> Optional[Type]:
        """只用于返回终端节点上一级节点的数据类型"""
        if self.get_node_type(node_index) != 0:
            return None
        path = self.get_node_path(node_index)
        parts: List[str] = self.split_path_to_parts(path)

        obj = self.uds_service
        for part in parts[:-1]:
            if dataclasses.is_dataclass(obj):
                obj = getattr(obj, part)
        _type: Type = obj._get_field_type(parts[-1])
        args = get_args(_type)
        return args[0]

    def get_obj(self, node_index: QModelIndex):
        path = self.get_node_path(node_index)
        parts: List[str] = self.split_path_to_parts(path)

        obj = self.uds_service
        for part in parts:
            if not isinstance(obj, list):
                obj = getattr(obj, part)
            else:
                obj = obj[int(part)]
        return obj

    @staticmethod
    def split_path_to_parts(path: str) -> List[str]:
        """
        将点分和索引路径拆分为属性名和纯数字索引列表。

        例如: "test.test.test[1]" -> ['test', 'test', 'test', '1']
        """

        # re.findall 遇到多个捕获组时，会返回元组列表：[('attr', ''), ('', 'index')]
        raw_parts: List[tuple[str, str]] = re.findall(r'([^.\[\]]+)|\[(\d+)]', path)

        # 清理步骤：使用列表推导式，从元组中提取唯一的非空字符串（属性名或纯数字索引）
        parts: List[str] = [p[0] or p[1] for p in raw_parts]

        return parts

    def get_obj_from_path(self, path):
        parts: List[str] = self.split_path_to_parts(path)

        obj = self.uds_service
        for part in parts:
            if not isinstance(obj, list):
                obj = getattr(obj, part)
            else:
                obj = obj[int(part)]
        return obj

    def get_node_info(self, node_index: QModelIndex):
        path = self.get_node_path(node_index)
        obj = self.get_obj_from_path(path)

        return path, obj

    def get_node_type(self, node_index: QModelIndex) -> int:
        """
        获取节点类型
        return 1：终端节点，0：终端上一级节点，-1：终端上二级及以上节点
        """
        return node_index.data(self.node_type_role)


# ------------------------------
# 自定义树形视图：处理bytes数据的交互
# ------------------------------
class DiagTreeView(QTreeView):

    clicked_node_data = Signal(bytes)
    status_bar_message = Signal(str)

    def __init__(self, parent=None, uds_service: UdsService = DEFAULT_SERVICES):
        super().__init__(parent)
        self.setModel(DiagTreeDataModel(uds_service=uds_service))
        self.expandAll()  # 展开所有节点
        self.resizeColumnToContents(0)  # 设置第0列显示全部文本，不会截断
        self._init_view()
        self._init_context_menu()

    def _init_view(self):
        """初始化视图配置"""
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)  # 单选
        self.setIndentation(20)  # 缩进距离
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 开启右键菜单

        # 绑定信号
        self.clicked.connect(self._on_node_clicked)
        self.doubleClicked.connect(self._on_sub_service_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def startDrag(self, supported_actions: Qt.DropAction):
        """重写拖拽开始逻辑：封装选中的节点数据"""
        # 1. 获取选中的节点索引
        selected_index = self.currentIndex()
        if not selected_index.isValid():
            return

        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            return
        if model.get_node_type(selected_index) != 1:  # 非终端节点
            return

        node_info = model.get_obj(selected_index)
        # 3. 封装拖拽数据（QMimeData）
        mime_data = QMimeData()
        # 自定义MIME类型（避免和其他拖拽冲突）
        mime_type = "application/x-diag-item"
        # 将数据转为字节流（支持复杂数据，这里先传文本）
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        # json_str = json.dumps(node_info, ensure_ascii=False, indent=0, default=json_default_converter)
        diagnosis_step_data = DiagnosisStepData()
        diagnosis_step_data.service = node_info.name
        diagnosis_step_data.send_data = node_info.payload
        diagnosis_step_data.step_type = DiagnosisStepTypeEnum.ExistingStep
        stream.writeQString(diagnosis_step_data.to_json())  # 写入诊断项名称
        mime_data.setData(mime_type, byte_array)

        # 4. 创建拖拽对象并启动拖拽
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(self.cursor().pos() - self.rect().topLeft())  # 拖拽热点
        # 执行拖拽（复制模式）
        drag.exec(Qt.CopyAction)

    def _init_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        # self.add_root_act = self.context_menu.addAction("添加服务")
        self.add_child_act = self.context_menu.addAction("添加子服务")
        self.context_menu.addSeparator()
        self.delete_act = self.context_menu.addAction("删除(子)服务")
        self.add_child_act.triggered.connect(self._add_operation_node)
        # self.add_root_act.triggered.connect(self._add_root_node)
        self.delete_act.triggered.connect(self._delete_operation_node)

    # def _get_node_level(self, index: QModelIndex) -> int:
    #     """计算给定 QModelIndex 的层级（深度），根节点为 0"""
    #     model = self.model()
    #     if not isinstance(model, DiagTreeDataModel):
    #         return 0xff
    #     return model.get_node_level(index)

    def _show_context_menu(self, pos: QPoint):
        """处理右键点击事件，根据节点深度动态启用/禁用菜单项"""
        # 获取被点击的 QModelIndex
        clicked_index = self.indexAt(pos)

        # 根节点/空白区域被点击
        if clicked_index.isValid():
            model = self.model()
            if not isinstance(model, DiagTreeDataModel):
                return
            node_type = model.get_node_type(clicked_index)

            if node_type == -1:
                # self.add_root_act.setEnabled(True)
                self.add_child_act.setEnabled(False)
                self.delete_act.setEnabled(False)
            elif node_type == 0:
                # self.add_root_act.setEnabled(True)
                self.add_child_act.setEnabled(True)
                self.delete_act.setEnabled(False)
            elif node_type == 1:
                self.add_child_act.setEnabled(False)
                self.delete_act.setEnabled(True)

        global_pos = self.mapToGlobal(pos)
        self.context_menu.exec(global_pos)

    def _on_sub_service_double_clicked(self, index: QModelIndex):
        """双击服务，为一级节点时获取节点数据并发送"""
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            return

        if model.get_node_type(index) != 1:
            return
        node_obj = model.get_obj(index)
        self.clicked_node_data.emit(node_obj.payload)

    def _on_node_clicked(self, index: QModelIndex):
        """节点点击：展示Hex字符串和字节长度"""
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            return
        path = model.get_node_path(index)
        obj = model.get_obj_from_path(path)
        node_type = model.get_node_type(index)
        if node_type == 1:
            payload = getattr(obj, 'payload', b'')
            if isinstance(payload, bytes):
                if len(payload) > 10:
                    display_text = f"{payload[:10].hex(' ')}...\n"
                else:
                    display_text = f"{payload[:10].hex(' ')}\n"
                self.status_bar_message.emit(display_text)
        # else:
        #     display_text = (
        #         f"Path：{path}"
        #     )

        # QMessageBox.information(self, "节点信息", display_text)

    def _add_operation_node(self):
        """添加子节点：调用对话框获取bytes数据"""
        current_index = self.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "提示", "请先选中一个节点再添加子节点！")
            return

        dialog = AddNodeDialog(parent=self, title="添加子服务")
        if dialog.exec() == QDialog.Accepted:
            node_name, custom_bytes = dialog.get_inputs()
            model = self.model()
            if isinstance(model, DiagTreeDataModel):
                success = model.add_operation_node(current_index, node_name, custom_bytes)
                if success:
                    self.expand(current_index)

    def _delete_operation_node(self):
        """删除节点"""
        current_index = self.currentIndex()
        model = self.model()
        if not isinstance(model, DiagTreeDataModel):
            QMessageBox.warning(self, "提示", "数据模型异常！")
            return
        success = model.delete_operation_node(current_index)
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

        # 点击的level 1层级，添加子服务必须带有数据
        if not hex_input:
            QMessageBox.warning(self, "数据不能为空", "节请输入合法的十六进制字符串（如1A3F、FF00）")
            self.lineEdit_Hex.setFocus()  # 聚焦到输入框重新输入
            return

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

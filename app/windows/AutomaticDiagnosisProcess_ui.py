# import pandas as pd
import logging
from typing import List, Any, Optional, Dict

from PySide6.QtCore import Qt, Slot, QDataStream, QIODevice, QModelIndex, QPoint, \
    QAbstractTableModel, QAbstractItemModel, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTreeView, QStyledItemDelegate, QTableView, QScrollBar, \
    QMenu, QAbstractItemView, QLineEdit, QFileIconProvider

from app.core.db_manager import DBManager
from app.resources.resources import IconEngine
from app.user_data import DiagnosisStepData, DiagnosisStepTypeEnum, DiagCase

logger = logging.getLogger('UDSTool.' + __name__)


class ColumnEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.no_edit_columns = {1}  # 禁止编辑的列号

    def createEditor(self, parent, option, index):
        # 判断当前列是否禁止编辑
        column_index = index.column()
        if column_index in self.no_edit_columns:
            return None  # 返回None = 不创建编辑器 → 禁止编辑

        if column_index == 0:
            return None

        # 允许编辑的列，创建默认编辑器（如QLineEdit）
        editor = QLineEdit(parent)
        editor.setContextMenuPolicy(Qt.NoContextMenu)
        return editor

    def setModelData(self, editor, model, index):
        if index.column() == 0:
            pass

        else:
            return super(ColumnEditDelegate, self).setModelData(editor, model, index)


class DiagProcessTableModel(QAbstractTableModel):
    def __init__(self, db_manager: DBManager):
        super().__init__()
        self.db_manager = db_manager
        self._data: List[DiagnosisStepData] = []
        self._data_dict: dict[int, DiagnosisStepData] = {}
        self._headers = DiagnosisStepData().get_attr_names()[1:11]
        self.current_case_id = None

    def clear(self):
        self.current_case_id = None
        self.beginResetModel()
        self._data.clear()
        self._data_dict.clear()
        self.endResetModel()

    def get_case_step_from_db(self, case_id):
        self.beginResetModel()
        self.current_case_id = case_id
        if not self.current_case_id:
            self._data.clear()
            self._data_dict.clear()
            self.endResetModel()

        self._data.clear()
        self._data_dict.clear()
        self._data = self.db_manager.case_step_db.get_case_steps_by_case_id(self.current_case_id)
        for __data in self._data:
            self._data_dict[__data.id] = __data
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        """重写表头方法，显示列名"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        row_tuple = self._data[row].to_tuple[1:11]
        col = index.column()

        # 显示数据
        if col == 0 and role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if row_tuple[col] == 'True' else Qt.CheckState.Unchecked
        elif role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return row_tuple[col]
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        # 1. 处理用户切换复选框状态 (CheckStateRole)
        if col == 0 and role == Qt.ItemDataRole.CheckStateRole:
            self._data[row].enable = bool(value)
            # 通知视图该索引的数据已改变
            self.dataChanged.emit(index, index, [role])
            return True

        # 2. 处理文本编辑 (EditRole)
        if role == Qt.ItemDataRole.EditRole:
            self._data[row].update_by_value(self._headers[col], value)
            self.db_manager.upsert_case_step(self._data[row])
            # 通知视图数据已改变
            self.dataChanged.emit(index, index, [role])
            return True

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
            # 在默认标志位上添加 Qt.ItemIsUserCheckable
            return flags | Qt.ItemFlag.ItemIsUserCheckable
        elif col == 1:
            return flags
        elif col in (2, 3):
            row = index.row()
            if self._data[row].step_type == DiagnosisStepTypeEnum.ExistingStep:
                return flags

        return flags | Qt.ItemFlag.ItemIsEditable

    def add_normal_test_step(self):
        test_step = DiagnosisStepData()
        # 插入新行到模型末尾（局部刷新）
        insert_row_idx = len(self._data)  # 新行的索引（末尾）
        test_step.step_sequence = insert_row_idx
        test_step.case_id = self.current_case_id
        # 通知视图：即将在insert_row_idx位置插入1行
        self.beginInsertRows(QModelIndex(), insert_row_idx, insert_row_idx)
        self._data.append(test_step)
        self._data_dict[test_step.id] = test_step
        self.db_manager.case_step_db.upsert_case_step(test_step)
        # 通知视图：插入操作完成
        self.endInsertRows()

    def add_existing_step(self, step_data: DiagnosisStepData):
        insert_row_idx = len(self._data)
        step_data.step_sequence = insert_row_idx
        step_data.case_id = self.current_case_id
        self.beginInsertRows(QModelIndex(), insert_row_idx, insert_row_idx)
        self._data.append(step_data)
        self._data_dict[step_data.id] = step_data
        self.db_manager.case_step_db.upsert_case_step(step_data)
        self.endInsertRows()


class DiagProcessTableView(QTableView):
    """DoIP追踪表格，优化布局和交互"""

    def __init__(self, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.model = DiagProcessTableModel(self.db_manager)
        self.setModel(self.model)
        self._auto_scroll = True  # 自动滚动开关
        self._headers = DiagnosisStepData().get_attr_names()

        self._init_ui()  # 初始化UI
        self._bind_scroll_listener()  # 绑定滚动监听
        self._init_data_context_menu()

    def clear(self):
        self.model.clear()

    def _init_ui(self):
        """初始化表格UI属性，确保铺满布局"""
        # 表格配置
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.CurrentChanged | QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.AnyKeyPressed)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)  # 隔行变色

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 隐藏垂直表头（可选，节省空间）
        self.verticalHeader().setVisible(False)

        self.setWordWrap(False)  # 禁止自动换行

        # 最后一列自适应剩余空间
        self.horizontalHeader().setStretchLastSection(True)

        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)  # 仅作为放置目标
        self.setDropIndicatorShown(True)  # 显示拖放指示器

        self.setItemDelegate(ColumnEditDelegate(self))

    def _bind_scroll_listener(self):
        """绑定滚动条监听，控制自动滚动"""
        scroll_bar: QScrollBar = self.verticalScrollBar()
        scroll_bar.valueChanged.connect(self._on_scroll_value_changed)

    # --------------------- 数据区域右键菜单（复制/清空） ---------------------
    def _init_data_context_menu(self):
        """初始化数据区域右键菜单：复制、清空"""
        # 设置表格视图的上下文菜单策略为自定义（表头的策略已单独设置，不冲突）
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 绑定数据区域右键菜单信号
        self.customContextMenuRequested.connect(self._show_data_context_menu)

    def _show_data_context_menu(self, pos):
        """显示数据区域右键菜单"""
        # 获取右键位置对应的模型索引（判断是否点击在数据行上）
        index = self.indexAt(pos)
        menu = QMenu(self)

        # 若点击在数据行上，添加复制相关选项
        if index.isValid():
            # 复制单元格内容
            add_normal_step_action = QAction("添加行", self)
            add_normal_step_action.triggered.connect(lambda: self.add_normal_test_step())
            menu.addAction(add_normal_step_action)

        add_normal_step_action = QAction("添加行", self)
        add_normal_step_action.triggered.connect(lambda: self.add_normal_test_step())
        menu.addAction(add_normal_step_action)

        # 显示菜单（转换为全局坐标）
        menu.exec(self.mapToGlobal(pos))

    def _clear_data(self):
        """清空数据"""
        pass

    @Slot(int)
    def _on_scroll_value_changed(self, value: int):
        """根据滚动条位置更新自动滚动状态"""
        scroll_bar = self.verticalScrollBar()
        self._auto_scroll = (value == scroll_bar.maximum())
        if self._auto_scroll:
            logger.debug("表格滚动到底部，开启自动滚动")

    def add_normal_test_step(self):
        self.model.add_normal_test_step()

    def add_existing_step(self, step_data: DiagnosisStepData):
        self.model.add_existing_step(step_data)

    def clear_test_step(self):
        pass

    @property
    def auto_scroll(self) -> bool:
        """获取自动滚动状态"""
        return self._auto_scroll

    @auto_scroll.setter
    def auto_scroll(self, state: bool):
        """设置自动滚动状态"""
        self._auto_scroll = state
        if state:
            self.scrollToBottom()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-diag-item"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-diag-item"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """TableView接收拖拽数据，解析字典"""
        mime_data = event.mimeData()
        mime_type = "application/x-diag-item"

        if self.model.current_case_id is None:
            return

        if not mime_data.hasFormat(mime_type):
            event.ignore()
            return

        # 1. 读取字节流中的JSON字符串
        byte_array = mime_data.data(mime_type)
        stream = QDataStream(byte_array, QIODevice.ReadOnly)
        json_str = stream.readQString()  # 读出JSON字符串

        diagnosis_step_data = DiagnosisStepData.from_json(json_str)

        self.add_existing_step(diagnosis_step_data)

        event.acceptProposedAction()


class DiagCaseNode:
    """树形节点封装类"""

    def __init__(self, case: DiagCase, parent: Optional["DiagCaseNode"] = None):
        self.case = case
        self.parent = parent
        self.children: List["DiagCaseNode"] = []

    def add_child(self, child: "DiagCaseNode"):
        self.children.append(child)

    def remove_child(self, child: "DiagCaseNode"):
        if child in self.children:
            self.children.remove(child)

    def child_count(self) -> int:
        return len(self.children)

    def child_at_index(self, index: int) -> Optional["DiagCaseNode"]:
        if 0 <= index < len(self.children):
            return self.children[index]
        return None

    def row_index(self) -> int:
        """获取自身在父节点中的行索引"""
        if self.parent:
            return self.parent.children.index(self)
        return 0


class DiagProcessCaseModel(QAbstractItemModel):
    """自定义树形模型（基于 QAbstractItemModel）"""
    # 自定义角色
    CaseIdRole = Qt.ItemDataRole.UserRole + 1
    CaseTypeRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.root_node = DiagCaseNode(DiagCase(id=-1, case_name="Root", type=1))
        # self.folder_icon = QFileIconProvider().icon(QFileIconProvider.IconType.Folder)
        self._build_tree_from_db()

    def _build_tree_from_db(self):
        """从数据库构建树形结构"""
        self.beginResetModel()
        # 清空现有节点
        self.root_node.children.clear()

        # 获取并排序案例
        config = self.db_manager.current_uds_config_db.get_active_config_name()
        cases = self.db_manager.uds_case_db.get_case_list_by_config(config)
        if not cases:
            self.endResetModel()
            return

        # # 按层级排序
        # case_df = pd.DataFrame([c.__dict__ for c in cases])
        # case_df_sorted = case_df.sort_values(by=["level"], ascending=True)
        # sorted_cases = [DiagCase.from_dict(row.to_dict()) for _, row in case_df_sorted.iterrows()]

        # 替代 Pandas：纯 Python 按 level 升序排序
        # 核心逻辑：使用 sorted + 自定义 key，按 level 字段排序
        sorted_cases = sorted(
            cases,
            key=lambda case: case.level,  # 按 level 升序
            reverse=False  # 显式指定升序（默认也是 False，可省略）
        )

        # 构建ID到节点的映射
        id_to_node: Dict[int, DiagCaseNode] = {}
        id_to_node[-1] = self.root_node

        # 先创建所有节点
        for case in sorted_cases:
            node = DiagCaseNode(case)
            id_to_node[case.id] = node

        # 建立父子关系
        for case in sorted_cases:
            node = id_to_node[case.id]
            parent_node = id_to_node.get(case.parent_id, self.root_node)
            parent_node.add_child(node)
            node.parent = parent_node

        self.endResetModel()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_node: DiagCaseNode = self.root_node
        if parent.isValid():
            parent_node = parent.internalPointer()

        child_node = parent_node.child_at_index(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_node: DiagCaseNode = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root_node or not parent_node:
            return QModelIndex()

        return self.createIndex(parent_node.row_index(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        parent_node: DiagCaseNode = self.root_node
        if parent.isValid():
            parent_node = parent.internalPointer()

        return parent_node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        node: DiagCaseNode = index.internalPointer()
        case = node.case

        # 显示文本
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return case.case_name

        # 图标
        elif role == Qt.ItemDataRole.DecorationRole:
            if case.type == 1:  # 分组显示文件夹图标
                return IconEngine.get_icon('folder')

        # 自定义角色（Case ID）
        elif role == self.CaseIdRole:
            return case.id

        # 自定义角色（Case 类型）
        elif role == self.CaseTypeRole:
            return case.type

        return None

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        node: DiagCaseNode = index.internalPointer()
        old_name = node.case.case_name
        new_name = str(value).strip()

        if new_name and new_name != old_name:
            self.beginResetModel()
            node.case.case_name = new_name
            self.db_manager.uds_case_db.upsert_case(node.case)  # 更新数据库
            self.endResetModel()
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        base_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        # 所有节点都可编辑
        return base_flags | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole and section == 0:
            return "UDS自动化Case"
        return None

    def add_case_node(self, parent_index: QModelIndex, is_group: bool = False) -> QModelIndex:
        """新增案例/分组节点"""
        # 创建新的DiagCase
        new_case = DiagCase(
            type=1 if is_group else 0,
            level=0,
            config_name=self.db_manager.current_uds_config_db.get_active_config_name()
        )
        new_case.id = self.db_manager.uds_case_db.upsert_case(new_case)
        new_case.case_name = f"请输入名称_{new_case.id}"

        # 处理父节点
        parent_node: DiagCaseNode = self.root_node
        if parent_index.isValid():
            parent_node = parent_index.internalPointer()
            new_case.parent_id = parent_node.case.id
            new_case.level = self._get_node_level(parent_index) + 1

        # 更新数据库
        self.db_manager.uds_case_db.upsert_case(new_case)

        # 添加到模型
        self.beginInsertRows(parent_index, parent_node.child_count(), parent_node.child_count())
        new_node = DiagCaseNode(new_case, parent_node)
        parent_node.add_child(new_node)
        self.endInsertRows()

        # 返回新节点的索引
        new_index = self.index(parent_node.child_count() - 1, 0, parent_index)
        return new_index

    def delete_node(self, index: QModelIndex) -> bool:
        """删除节点（含子节点）"""
        if not index.isValid():
            return False

        node: DiagCaseNode = index.internalPointer()
        parent_node = node.parent
        if not parent_node:
            return False

        # 递归删除所有子节点（数据库）
        def _delete_children(child_node: DiagCaseNode):
            for child in child_node.children:
                _delete_children(child)
                self.db_manager.uds_case_db.delete_case_by_id(child.case.id)

        _delete_children(node)

        # 删除当前节点
        self.beginRemoveRows(self.parent(index), node.row_index(), node.row_index())
        parent_node.remove_child(node)
        self.db_manager.uds_case_db.delete_case_by_id(node.case.id)
        self.endRemoveRows()
        return True

    def _get_node_level(self, index: QModelIndex) -> int:
        """获取节点层级"""
        level = 0
        current = index
        while current.parent().isValid():
            level += 1
            current = current.parent()
        return level

    def refresh_model(self):
        """刷新模型数据"""
        self._build_tree_from_db()


class DiagProcessCaseTreeView(QTreeView):
    clicked_case_id = Signal(int)

    def __init__(self, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.model = DiagProcessCaseModel(db_manager, self)
        self.setModel(self.model)
        self._right_click_pos = None

        # 视图初始化
        self._init_view()
        self._init_context_menu()
        self.clicked.connect(self._on_node_clicked)

        # 初始展开所有节点
        self.expandAll()
        self.resizeColumnToContents(0)

    def refresh(self):
        self.model._build_tree_from_db()

    def _init_view(self):
        """初始化视图配置"""
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.setIndentation(20)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 双击编辑
        self.setEditTriggers(QTreeView.EditTrigger.DoubleClicked)
        # 绑定右键菜单信号
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _init_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        self.add_case_act = self.context_menu.addAction("添加Case")
        self.add_group_act = self.context_menu.addAction("添加分组")
        self.delete_act = self.context_menu.addAction("删除")

        # 绑定菜单事件
        self.add_case_act.triggered.connect(lambda: self._add_node(is_group=False))
        self.add_group_act.triggered.connect(lambda: self._add_node(is_group=True))
        self.delete_act.triggered.connect(self._delete_node)

    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单（根据节点类型动态控制菜单）"""
        clicked_index = self.indexAt(pos)
        self._right_click_pos = pos
        # 重置菜单状态
        self.add_case_act.setEnabled(False)
        self.add_group_act.setEnabled(False)
        self.delete_act.setEnabled(False)

        if clicked_index.isValid():
            # 获取节点类型
            node_type = clicked_index.data(self.model.CaseTypeRole)
            if node_type == 1:  # 分组节点
                self.add_case_act.setEnabled(True)
                self.add_group_act.setEnabled(True)
                self.delete_act.setEnabled(True)
            elif node_type == 0:  # 案例节点
                self.delete_act.setEnabled(True)
        else:
            self.add_case_act.setEnabled(True)
            self.add_group_act.setEnabled(True)

        # 显示菜单
        self.context_menu.exec(self.mapToGlobal(pos))

    def _on_node_clicked(self, index: QModelIndex):
        node = index.internalPointer()
        case = node.case
        if case.type == 0:
            self.clicked_case_id.emit(case.id)

    def _add_node(self, is_group: bool):
        """添加案例/分组节点"""
        current_index = self.indexAt(self._right_click_pos)
        # 新增节点
        new_index = self.model.add_case_node(current_index, is_group)
        if new_index.isValid():
            # 展开父节点
            self.expand(current_index)
            # 立即进入编辑状态
            self.edit(new_index)

    def _delete_node(self):
        """删除选中节点"""
        current_index = self.indexAt(self._right_click_pos)
        if current_index.isValid():
            self.model.delete_node(current_index)

    def get_node_level(self, index: QModelIndex) -> int:
        """获取节点层级（对外暴露）"""
        return self.model._get_node_level(index)

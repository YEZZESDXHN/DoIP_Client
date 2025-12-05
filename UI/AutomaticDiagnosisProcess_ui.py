import logging

from PySide6.QtCore import QEvent, Qt, Slot
from PySide6.QtGui import QAction, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QTreeView, QSizePolicy, QWidget, QStyledItemDelegate, QTableView, QScrollBar, \
    QMenu, QAbstractItemView
from user_data import DiagnosisStepData

logger = logging.getLogger("UiCustom.DiagnosisProcess")

class DiagTreeViewComboBox(QComboBox):
    """自定义ComboBox，下拉显示TreeView"""

    def __init__(self, model, parent=None, ):
        super().__init__(parent)
        # self.setView(QTreeView())
        # self.tree_view = self.view()
        self.view()
        self.tree_view = self.view()

        self.tree_view.setHeaderHidden(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setItemsExpandable(True)
        self.tree_view.expandAll()

        self.setModel(model)


        self.setMinimumContentsLength(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def showPopup(self):
        self.tree_view.expandAll()
        self.tree_view.adjustSize()
        popup = self.findChild(QWidget, "QComboBoxPrivateContainer")
        if popup:
            popup.setMinimumWidth(max(self.width(), self.tree_view.width()))
        super().showPopup()

    def hidePopup(self):
        if self.currentIndex() != -1:
            self.activated.emit(self.currentIndex())
        super().hidePopup()


class TreeViewDelegate(QStyledItemDelegate):
    """自定义委托，管理TreeView下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_models = {}  # (行号, 列号) -> TreeModel
        self.current_editor = None

    def set_tree_model_for_index(self, index, tree_model):
        """为指定单元格设置TreeView模型"""
        key = (index.row(), index.column())
        self.tree_models[key] = tree_model

    def createEditor(self, parent, option, index):
        key = (index.row(), index.column())
        if key not in self.tree_models:
            return super().createEditor(parent, option, index)

        editor = DiagTreeViewComboBox(parent)
        editor.activated.connect(lambda: self.commitData.emit(editor))
        editor.activated.connect(lambda: self.closeEditor.emit(editor))

        self.current_editor = editor
        return editor

    def setEditorData(self, editor, index):
        if not isinstance(editor, DiagTreeViewComboBox):
            super().setEditorData(editor, index)
            return

        current_value = index.data(Qt.ItemDataRole.DisplayRole)
        if current_value is None or current_value == "":
            return

        model = editor.model()
        if isinstance(model, QStandardItemModel):
            root_item = model.invisibleRootItem()
            root_index = root_item.index()
            self._select_item_in_tree(model, root_index, current_value, editor)

    def setModelData(self, editor, model, index):
        if not isinstance(editor, DiagTreeViewComboBox):
            super().setModelData(editor, model, index)
            return

        selected_index = editor.tree_view.currentIndex()
        if selected_index.isValid():
            selected_value = selected_index.data(Qt.ItemDataRole.DisplayRole)
            model.setData(index, selected_value, Qt.ItemDataRole.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        if isinstance(editor, DiagTreeViewComboBox):
            editor.setGeometry(option.rect)
        else:
            super().updateEditorGeometry(editor, option, index)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if index.column() == 1:
                self.parent().edit(index)
                if self.current_editor:
                    self.current_editor.showPopup()
                return True
        return super().editorEvent(event, model, option, index)

    def _select_item_in_tree(self, model, parent_index, target_value, editor):
        for row in range(model.rowCount(parent_index)):
            current_index = model.index(row, 0, parent_index)
            if not current_index.isValid():
                continue

            current_value = current_index.data(Qt.ItemDataRole.DisplayRole)
            if current_value == target_value:
                editor.tree_view.setCurrentIndex(current_index)
                return True

            if model.hasChildren(current_index):
                if self._select_item_in_tree(model, current_index, target_value, editor):
                    return True
        return False

class DiagProcessTableModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHorizontalHeaderLabels(DiagnosisStepData().get_attr_names())

    def add_row_data(self):
        self.appendRow(DiagnosisStepData().to_tuple())


class DiagProcessTableView(QTableView):
    """DoIP追踪表格，优化布局和交互"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_scroll = True  # 自动滚动开关
        self._headers = DiagnosisStepData().get_attr_names()


        self._init_ui()  # 初始化UI
        self._bind_scroll_listener()  # 绑定滚动监听
        self._init_data_context_menu()

    def _init_ui(self):
        """初始化表格UI属性，确保铺满布局"""
        # 表格配置
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.CurrentChanged |
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)  # 隔行变色

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 隐藏垂直表头（可选，节省空间）
        self.verticalHeader().setVisible(False)

        self.setWordWrap(False)  # 禁止自动换行

        # 最后一列自适应剩余空间
        self.horizontalHeader().setStretchLastSection(True)

        self.tree_view_delegate = TreeViewDelegate(self)
        self.setItemDelegateForColumn(1, self.tree_view_delegate)


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
            copy_cell_action = QAction("复制单元格内容", self)
            copy_cell_action.triggered.connect(lambda: self._copy_cell_data(index))
            menu.addAction(copy_cell_action)

            # 复制整行内容
            copy_row_action = QAction("复制整行内容", self)
            copy_row_action.triggered.connect(lambda: self._copy_row_data(index.row()))
            menu.addAction(copy_row_action)

            # 分隔线
            menu.addSeparator()

        export_text_action = QAction("导出到text", self)
        export_text_action.triggered.connect(lambda: self.export_to_text())
        menu.addAction(export_text_action)

        export_excel_action = QAction("导出到Excel", self)
        export_excel_action.triggered.connect(lambda: self.export_to_excel())
        menu.addAction(export_excel_action)

        # 清空数据选项（无论是否点击在数据行上都显示）
        clear_action = QAction("清空表格数据", self)
        clear_action.triggered.connect(self._clear_data)
        menu.addAction(clear_action)

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

    def add_test_step(self, data):
        model = self.model()
        if isinstance(model, DiagProcessTableModel):
            model.add_empty_row_data()

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


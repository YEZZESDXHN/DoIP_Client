# from PySide6.QtCore import QEvent, Qt
# from PySide6.QtWidgets import QComboBox, QTreeView, QSizePolicy, QWidget, QStyledItemDelegate
# from treeView_ui import DiagTreeView
#
# class TreeViewComboBox(QComboBox):
#     """自定义ComboBox，下拉列表中显示TreeView"""
#
#     def __init__(self, diag_tree_view: DiagTreeView, parent=None):
#         super().__init__(parent)
#
#         self.tree_view = diag_tree_view
#
#         # 配置TreeView
#         self.tree_view.setHeaderHidden(True)
#         self.tree_view.setRootIsDecorated(True)
#         self.tree_view.setItemsExpandable(True)
#         self.tree_view.expandAll()  # 展开所有节点
#
#         # 设置下拉列表的大小
#         self.setMinimumContentsLength(20)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
#
#         # 关键设置：允许弹出时自动获取焦点
#         self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
#
#     def showPopup(self):
#         """重写显示弹出框的方法，确保TreeView正确显示"""
#         self.tree_view.expandAll()
#         # 调整下拉框大小以适应内容
#         self.tree_view.adjustSize()
#         # 确保下拉框大小合适
#         popup = self.findChild(QWidget, "QComboBoxPrivateContainer")
#         if popup:
#             popup.setMinimumWidth(self.width())
#         super().showPopup()
#
#     def hidePopup(self):
#         """重写隐藏弹出框的方法，确保数据正确提交"""
#         # 先提交数据再隐藏
#         if self.currentIndex() != -1:
#             self.activated.emit(self.currentIndex())
#         super().hidePopup()
#
#
# class TreeViewDelegate(QStyledItemDelegate):
#     """自定义委托，用于在TableView中显示带TreeView的下拉框"""
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.tree_models = {}  # 存储每个单元格的TreeView模型
#         self.current_editor = None
#
#     def set_tree_model_for_index(self, index, tree_model):
#         """为指定索引的单元格设置TreeView模型"""
#         key = (index.row(), index.column())
#         self.tree_models[key] = tree_model
#
#     def createEditor(self, parent, option, index):
#         """创建编辑器（带TreeView的ComboBox）"""
#         key = (index.row(), index.column())
#         if key not in self.tree_models:
#             return super().createEditor(parent, option, index)
#
#         editor = TreeViewComboBox(parent)
#         editor.set_tree_model(self.tree_models[key])
#
#         # 连接信号，确保选择后提交数据
#         editor.activated.connect(lambda: self.commitData.emit(editor))
#         editor.activated.connect(lambda: self.closeEditor.emit(editor))
#
#         self.current_editor = editor
#         return editor
#
#     def setEditorData(self, editor, index):
#         """将模型数据设置到编辑器中"""
#         if not isinstance(editor, TreeViewComboBox):
#             super().setEditorData(editor, index)
#             return
#
#         current_value = index.data(Qt.ItemDataRole.DisplayRole)
#         if current_value is None or current_value == "":
#             return
#
#         model = editor.model()
#         root_index = model.invisibleRootItem().index()
#         self._select_item_in_tree(model, root_index, current_value, editor)
#
#     def setModelData(self, editor, model, index):
#         """将编辑器中的数据保存到模型中"""
#         if not isinstance(editor, TreeViewComboBox):
#             super().setModelData(editor, model, index)
#             return
#
#         selected_index = editor.tree_view.currentIndex()
#         if selected_index.isValid():
#             selected_value = selected_index.data(Qt.ItemDataRole.DisplayRole)
#             model.setData(index, selected_value, Qt.ItemDataRole.DisplayRole)
#
#     def updateEditorGeometry(self, editor, option, index):
#         """更新编辑器的几何位置"""
#         if isinstance(editor, TreeViewComboBox):
#             editor.setGeometry(option.rect)
#         else:
#             super().updateEditorGeometry(editor, option, index)
#
#     def editorEvent(self, event, model, option, index):
#         """重写编辑器事件，实现单击弹出下拉框"""
#         if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
#             # 检查是否是目标列（第二列）
#             if index.column() == 1:
#                 # 触发编辑模式
#                 self.parent().edit(index)
#                 # 如果编辑器已创建，直接显示下拉框
#                 if self.current_editor:
#                     self.current_editor.showPopup()
#                 return True
#         return super().editorEvent(event, model, option, index)
#
#     def _select_item_in_tree(self, model, parent_index, target_value, editor):
#         """递归查找并选中TreeView中的项目"""
#         for row in range(model.rowCount(parent_index)):
#             current_index = model.index(row, 0, parent_index)
#             if not current_index.isValid():
#                 continue
#
#             current_value = current_index.data(Qt.ItemDataRole.DisplayRole)
#             if current_value == target_value:
#                 editor.tree_view.setCurrentIndex(current_index)
#                 return True
#
#             if model.hasChildren(current_index):
#                 if self._select_item_in_tree(model, current_index, target_value, editor):
#                     return True
#
#         return False


import sys
from PySide6.QtCore import Qt, QModelIndex, QEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QTreeView,
                               QStyledItemDelegate, QComboBox, QAbstractItemView,
                               QVBoxLayout, QWidget, QSizePolicy, QPushButton,
                               QHBoxLayout, QMessageBox)
from PySide6.QtGui import QStandardItemModel, QStandardItem


class TreeViewComboBox(QComboBox):
    """自定义ComboBox，下拉显示TreeView"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QTreeView())
        self.tree_view = self.view()

        self.tree_view.setHeaderHidden(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setItemsExpandable(True)
        self.tree_view.expandAll()

        self.setMinimumContentsLength(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_tree_model(self, model):
        self.setModel(model)
        self.tree_view.setModel(model)

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

        editor = TreeViewComboBox(parent)
        editor.set_tree_model(self.tree_models[key])
        editor.activated.connect(lambda: self.commitData.emit(editor))
        editor.activated.connect(lambda: self.closeEditor.emit(editor))

        self.current_editor = editor
        return editor

    def setEditorData(self, editor, index):
        if not isinstance(editor, TreeViewComboBox):
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
        if not isinstance(editor, TreeViewComboBox):
            super().setModelData(editor, model, index)
            return

        selected_index = editor.tree_view.currentIndex()
        if selected_index.isValid():
            selected_value = selected_index.data(Qt.ItemDataRole.DisplayRole)
            model.setData(index, selected_value, Qt.ItemDataRole.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        if isinstance(editor, TreeViewComboBox):
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("空表格 + 逐行添加（带TreeView下拉）")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.row_count = 0  # 记录当前行数（用于新增行号）

    def init_ui(self):
        """初始化空表格（只显示标题）"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 布局：按钮 + 表格
        main_layout = QVBoxLayout(central_widget)

        # 按钮区域（添加行、删除行）
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加一行")
        self.add_btn.clicked.connect(self.add_new_row)  # 绑定添加行事件
        self.del_btn = QPushButton("删除选中行")
        self.del_btn.clicked.connect(self.delete_selected_row)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        main_layout.addLayout(btn_layout)

        # 1. 创建空表格模型（0行2列，只显示表头）
        self.table_model = QStandardItemModel(0, 2)  # 关键：初始行数设为0
        self.table_model.setHorizontalHeaderLabels(["类别", "选择项"])  # 只显示标题

        # 2. 创建表格视图
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        # 表格配置
        self.table_view.setEditTriggers(
            QAbstractItemView.EditTrigger.CurrentChanged |
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setColumnWidth(0, 200)
        self.table_view.setColumnWidth(1, 300)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        main_layout.addWidget(self.table_view)

        # 3. 设置委托（下拉TreeView）
        self.delegate = TreeViewDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(1, self.delegate)

    def create_tree_model_for_category(self, category):
        """根据类别创建TreeView模型（复用之前的逻辑）"""
        model = QStandardItemModel()
        root = model.invisibleRootItem()

        if category == "电子产品":
            computers = QStandardItem("电脑设备")
            computers.appendRow(QStandardItem("笔记本电脑"))
            computers.appendRow(QStandardItem("台式电脑"))
            root.appendRow(computers)
        elif category == "办公用品":
            stationery = QStandardItem("文具")
            stationery.appendRow(QStandardItem("笔记本"))
            stationery.appendRow(QStandardItem("笔类"))
            root.appendRow(stationery)
        elif category == "图书资料":
            books = QStandardItem("书籍")
            books.appendRow(QStandardItem("计算机科学"))
            books.appendRow(QStandardItem("文学小说"))
            root.appendRow(books)
        elif category == "生活用品":
            kitchen = QStandardItem("厨房用品")
            kitchen.appendRow(QStandardItem("厨具"))
            kitchen.appendRow(QStandardItem("餐具"))
            root.appendRow(kitchen)

        return model

    def add_new_row(self):
        """添加一行数据（核心方法）"""
        # 1. 定义新增行的类别（可循环切换，或让用户输入，这里用循环示例）
        categories = ["电子产品", "办公用品", "图书资料", "生活用品"]
        current_category = categories[self.row_count % len(categories)]  # 循环切换类别

        # 2. 创建当前行的两个列项
        category_item = QStandardItem(current_category)
        category_item.setEditable(False)  # 类别列不可编辑
        select_item = QStandardItem("")  # 选择项初始为空

        # 3. 追加一行到表格（关键：appendRow 自动增加行数）
        self.table_model.appendRow([category_item, select_item])

        # 4. 给当前行的第1列（选择项）绑定对应的TreeView模型
        current_row = self.table_model.rowCount() - 1  # 刚添加的行号（最后一行）
        tree_model = self.create_tree_model_for_category(current_category)
        self.delegate.set_tree_model_for_index(
            self.table_model.index(current_row, 1),  # 第current_row行第1列
            tree_model
        )

        # 5. 更新行数计数器
        self.row_count += 1

        # 6. 自动滚动到新增行（优化体验）
        self.table_view.scrollToBottom()

        QMessageBox.information(self, "提示", f"已添加一行（类别：{current_category}）")

    def delete_selected_row(self):
        """删除选中的行"""
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "警告", "请先选中一行！")
            return

        # 获取选中行的行号（所有选中单元格的行号相同）
        selected_row = selected_indexes[0].row()

        # 删除行（同时删除对应的TreeView模型）
        self.table_model.removeRow(selected_row)
        # 删除委托中存储的TreeView模型
        del self.delegate.tree_models[(selected_row, 1)]

        # 更新行数计数器
        self.row_count = max(0, self.row_count - 1)

        QMessageBox.information(self, "提示", f"已删除第{selected_row}行")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
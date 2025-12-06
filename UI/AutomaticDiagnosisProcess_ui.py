import json
import logging

from PySide6.QtCore import QEvent, Qt, Slot, QDataStream, QIODevice, QModelIndex, QSize, QRect, QPoint
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem, QPainter, QMouseEvent
from PySide6.QtWidgets import QComboBox, QTreeView, QSizePolicy, QWidget, QStyledItemDelegate, QTableView, QScrollBar, \
    QMenu, QAbstractItemView, QLineEdit, QCheckBox, QStyle, QApplication, QStyleOptionButton
from user_data import DiagnosisStepData, DiagnosisStepTypeEnum
from utils import json_custom_decoder

logger = logging.getLogger("UiCustom.DiagnosisProcess")


class ColumnEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.no_edit_columns = {1}  # 禁止编辑的列号

    def paint(self, painter, option, index):
        column_index = index.column()
        if column_index == 0:
            check_style = QStyleOptionButton()
            check_style.rect = option.rect
            if index.data() is True:
                check_style.state = QStyle.State_Enabled | QStyle.State_On
            elif index.data() is False:
                check_style.state = QStyle.State_Enabled | QStyle.State_Off
            QApplication.style().drawControl(QStyle.CE_CheckBox, check_style, painter)

        else:
            return super(ColumnEditDelegate, self).paint(painter, option, index)
    def createEditor(self, parent, option, index):
        # 判断当前列是否禁止编辑
        column_index = index.column()
        if column_index in self.no_edit_columns:
            return None  # 返回None = 不创建编辑器 → 禁止编辑

        if column_index == 0:
            return QCheckBox(parent)
        # 允许编辑的列，创建默认编辑器（如QLineEdit）
        return QLineEdit(parent)

    def setModelData(self, editor, model, index):
        if index.column() == 0:
            if isinstance(editor, QCheckBox):
                model.setData(index, bool(editor.isChecked()))
        else:
            return super(ColumnEditDelegate, self).setModelData(editor, model, index)

class DiagProcessTableModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHorizontalHeaderLabels(DiagnosisStepData().get_attr_names())

    def add_normal_test_step(self):
        item_list = [QStandardItem(str(item)) for item in DiagnosisStepData().to_tuple()]
        self.appendRow(item_list)

    def add_existing_step(self, step_data: DiagnosisStepData):
        item_list = [QStandardItem(str(item)) for item in step_data.to_tuple()]
        self.appendRow(item_list)





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
        model = self.model()
        if isinstance(model, DiagProcessTableModel):
            model.add_normal_test_step()

    def add_existing_step(self, step_data: DiagnosisStepData):
        model = self.model()
        if isinstance(model, DiagProcessTableModel):
            model.add_existing_step(step_data)
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

        if not mime_data.hasFormat(mime_type):
            event.ignore()
            return

        # 1. 读取字节流中的JSON字符串
        byte_array = mime_data.data(mime_type)
        stream = QDataStream(byte_array, QIODevice.ReadOnly)
        json_str = stream.readQString()  # 读出JSON字符串

        diagnosis_step_data = DiagnosisStepData()
        diagnosis_step_data.from_json(json_str)


        self.add_existing_step(diagnosis_step_data)

        event.acceptProposedAction()


import os
from datetime import datetime
from enum import IntEnum, Enum
from typing import List, Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QEvent, Signal, QTimer, Slot
from PySide6.QtGui import QMouseEvent, QContextMenuEvent, QAction, QCursor, QColor
from PySide6.QtWidgets import QWidget, QTableView, QAbstractItemView, QMenu, QFileDialog, QStyledItemDelegate, \
    QStyleOptionButton, QStyle, QApplication, QHeaderView, QVBoxLayout

from app.core.db_manager import DBManager
from app.resources.resources import IconEngine
from app.ui.ExternalScriptPanel import Ui_ExternalScript_Panel
from app.user_data import ExternalScriptConfig, ExternalScriptRunState, ExternalScriptsRunState


class ExternalScriptTableCol(IntEnum):
    enable = 0
    name = 1
    path = 2
    state = 3


class ExternalScriptTableDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        """自定义绘制"""

        if index.column() == ExternalScriptTableCol.enable:
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
        elif index.column() == ExternalScriptTableCol.state:
            value = index.data(Qt.ItemDataRole.EditRole)
            if isinstance(value, str):
                super().paint(painter, option, index)
        # 2. 其他类型，使用默认绘制
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        """处理点击事件，实现单击切换"""

        if index.column() == ExternalScriptTableCol.enable:
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
        if index.column() == ExternalScriptTableCol.enable:
            value = index.data(Qt.ItemDataRole.EditRole)
            if isinstance(value, bool):
                return None  # 这一步很关键！防止双击弹出空白框
        elif index.column() == ExternalScriptTableCol.state:
            return None
        return super().createEditor(parent, option, index)


class ExternalScriptTableModel(QAbstractTableModel):

    def __init__(self, db_manager: DBManager, external_scripts: List[ExternalScriptConfig], parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.external_scripts = external_scripts

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.external_scripts)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 4

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        item = self.external_scripts[index.row()]
        col = index.column()

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == ExternalScriptTableCol.enable:
                return item.enable
            if col == ExternalScriptTableCol.name:
                return item.name
            if col == ExternalScriptTableCol.path:
                return item.path
            if col == ExternalScriptTableCol.state:
                return item.state

        if role == Qt.ItemDataRole.BackgroundRole:
            if col == ExternalScriptTableCol.state:
                if item.state in (ExternalScriptRunState.OK, ExternalScriptRunState.Running):
                    return QColor("#CCFFCC")
                elif item.state in (ExternalScriptRunState.TESTS_FAILED,
                                    ExternalScriptRunState.NO_TESTS_COLLECTED,
                                    ExternalScriptRunState.INTERNAL_ERROR,
                                    ExternalScriptRunState.ScriptLoadingFailed):
                    return QColor("#FFCCCC")
                # elif item.state == ExternalScriptRunState.RunStopping:
                #     return QColor("yellow")

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        item = self.external_scripts[index.row()]
        col = index.column()

        if col == ExternalScriptTableCol.enable:
            if isinstance(value, bool):
                item.enable = value
        if col == ExternalScriptTableCol.name:
            if isinstance(value, str):
                item.name = value
        if col == ExternalScriptTableCol.path:
            if isinstance(value, str):
                item.path = value
                filename = os.path.basename(value)
                name = os.path.splitext(filename)[0]
                item.name = name
        if col == ExternalScriptTableCol.state:
            if isinstance(value, str):
                item.path = value
        item.state = ExternalScriptRunState.Idle
        self.db_manager.external_script_db.save_external_script(item)
        self.dataChanged.emit(index, index, [role])
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return [" ", "Name", "Path", ""][section]

    def add_script(self, config):
        row = self.rowCount()
        script = ExternalScriptConfig()
        script.config = config
        self.beginInsertRows(QModelIndex(), row, row)
        sql_id = self.db_manager.external_script_db.save_external_script(script)
        script.sql_id = sql_id
        self.external_scripts.append(script)
        self.endInsertRows()

    def delete_script(self, row):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del_num = self.db_manager.external_script_db.delete_external_script_by_sql_id(self.external_scripts[row].sql_id)
            self.external_scripts.pop(row)
            self.endRemoveRows()

    def update_script_state(self, row_index, new_state):
        """修改指定行的state，并触发视图更新"""
        # 1. 检查行索引是否合法
        if 0 <= row_index < len(self.external_scripts):
            self.external_scripts[row_index].state = new_state
            model_index = self.index(row_index, ExternalScriptTableCol.state)
            self.dataChanged.emit(model_index, model_index)


class ExternalScriptTableView(QTableView):
    """自定义表格视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 默认规则：双击/选中后单击 均可编辑
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

    def mousePressEvent(self, event: QMouseEvent):
        """单击Path列单元格弹出文件选择框，其他列保留默认编辑逻辑"""
        index = self.indexAt(event.pos())

        # 仅拦截 Path 列的左键单击事件
        if index.isValid() and index.column() == ExternalScriptTableCol.path and event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog(index)
            return  # 阻止Path列触发默认的"选中单击编辑"

        # 其他列/情况执行默认逻辑（保留编辑能力）
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """仅拦截Path列的双击事件，其他列保留默认双击编辑"""
        index = self.indexAt(event.pos())

        if index.isValid() and index.column() == ExternalScriptTableCol.path and event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog(index)  # 双击Path列也弹文件选择框（可选）
            return

        # 其他列执行默认双击编辑
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单：为Path列添加手动编辑选项"""
        index = self.indexAt(event.pos())
        if not index.isValid():
            super().contextMenuEvent(event)
            return

        # 为Path列定制右键菜单
        if index.column() == ExternalScriptTableCol.path:
            menu = QMenu(self)

            # 1. 选择文件选项
            select_file_action = QAction("选择文件", self)
            select_file_action.triggered.connect(lambda: self._open_file_dialog(index))
            menu.addAction(select_file_action)

            # 2. 手动编辑路径选项
            edit_path_action = QAction("手动编辑路径", self)
            edit_path_action.triggered.connect(lambda: self.edit(index))
            menu.addAction(edit_path_action)

            # 3. 清空路径选项（可选）
            clear_path_action = QAction("清空路径", self)
            clear_path_action.triggered.connect(lambda: self.model().setData(
                index, "", Qt.ItemDataRole.EditRole
            ))
            menu.addAction(clear_path_action)

            menu.exec(event.globalPos())
        else:
            # 其他列使用默认右键菜单（保留编辑能力）
            super().contextMenuEvent(event)

    def _open_file_dialog(self, index: QModelIndex):
        """封装文件选择对话框逻辑，便于复用"""
        # 获取当前单元格的路径作为初始目录
        current_path = index.data() or os.getcwd()
        abs_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择默认刷写文件",
            current_path,
            "Python File (*.py);;"
        )

        if abs_path:
            try:
                # 计算相对路径（以程序运行目录为基准）
                rel_path = os.path.relpath(abs_path, os.getcwd())
                file_path = rel_path
            except ValueError:
                # 跨盘符时使用绝对路径
                file_path = abs_path

            # 更新模型数据
            self.model().setData(index, file_path, Qt.ItemDataRole.EditRole)
            self.update(index)


class ExternalScriptPanel(Ui_ExternalScript_Panel, QWidget):
    signal_config_update = Signal()

    def __init__(self, db_manager: DBManager, config_name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.config_name = config_name
        self.db_manager = db_manager
        self.external_scripts: List[ExternalScriptConfig] = self.db_manager.external_script_db.get_external_script_list_by_config(
            self.config_name)
        self.external_script_table_mode = ExternalScriptTableModel(external_scripts=self.external_scripts,
                                                                   db_manager=self.db_manager)
        self.tableView_ExternalScript = self._setup_view(self.scrollAreaWidgetContents, self.external_script_table_mode,
                                                         ExternalScriptTableView())
        self.tableView_ExternalScript.setModel(self.external_script_table_mode)
        self.tableView_ExternalScript.setItemDelegate(ExternalScriptTableDelegate(self.tableView_ExternalScript))
        self.signal_config_update.connect(self.load_external_scripts)
        self._init_data_context_menu()
        self.pushButton_stop.setIcon(IconEngine.get_icon("stop", 'red'))
        self.pushButton_start.setIcon(IconEngine.get_icon("start", 'blue'))
        self.pushButton_stop.setDisabled(True)

        self.pushButton_start.clicked.connect(self.on_run_script)

        self.run_timer = QTimer()  # 实时计时定时器
        self.run_timer.setInterval(100)  # 计时精度：100ms，0.1秒刷新一次，足够流畅
        self.run_timer.timeout.connect(self.update_run_time)  # 定时刷新时间
        self.run_start_dt = None

        self.scripts_run_state = ExternalScriptsRunState.running

    def update_run_time(self):
        if self.run_start_dt:
            duration = (datetime.now() - self.run_start_dt).total_seconds()
            time_str = f"{int(duration // 60):02d}:{duration % 60:.2f}"
            self.label_State.setText(f"{self.scripts_run_state} |  {time_str}")

    def update_scripts_run_state(self, state):
        self.scripts_run_state = state
        if state == ExternalScriptsRunState.stopping:
            self.pushButton_stop.setDisabled(True)

    def on_run_finish(self, state: ExternalScriptsRunState):
        self.run_timer.stop()
        duration = (datetime.now() - self.run_start_dt).total_seconds()
        time_str = f"{int(duration // 60):02d}:{duration % 60:.2f}"
        self.label_State.setText(f"{state.value} | {time_str}")

        if state == ExternalScriptsRunState.passed:
            self.set_run_state_label_color("green")
        else:
            self.set_run_state_label_color("red")

        self.pushButton_stop.setDisabled(True)
        self.pushButton_start.setDisabled(False)

    def update_script_run_state(self, state: ExternalScriptRunState, row_index: int):
        self.external_script_table_mode.update_script_state(row_index, state)
        # if state == ExternalScriptRunState.RunStopping:
        #     self.pushButton_stop.setDisabled(True)

    @Slot()
    def on_run_script(self):
        self.run_start_dt = datetime.now()
        self.run_timer.start()
        self.scripts_run_state = ExternalScriptsRunState.running
        self.set_run_state_label_color("orange")

        self.pushButton_stop.setDisabled(False)
        self.pushButton_start.setDisabled(True)

    def set_run_state_label_color(self, color):
        self.label_State.setStyleSheet(f"QLabel {{ color: {color}; }}")

    def _init_data_context_menu(self):
        """初始化数据区域右键菜单：复制、清空"""
        # 设置表格视图的上下文菜单策略为自定义（表头的策略已单独设置，不冲突）
        self.tableView_ExternalScript.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 绑定数据区域右键菜单信号
        self.tableView_ExternalScript.customContextMenuRequested.connect(self._show_data_context_menu)

    def _show_data_context_menu(self, pos):
        """显示数据区域右键菜单"""
        menu = QMenu(self)
        index = self.tableView_ExternalScript.indexAt(pos)
        add_action = QAction("add", self)
        add_action.triggered.connect(self.add_script)
        menu.addAction(add_action)

        if index.isValid():
            del_action = QAction("del", self)
            del_action.triggered.connect(lambda: self.delete_script(index.row()))
            menu.addAction(del_action)

        menu.exec(QCursor.pos())

    def _setup_view(self, parent_widget, model, view=None):
        if not view:
            view = QTableView()
        view.setModel(model)

        # 常用视图设置
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QTableView.SelectRows)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header = view.horizontalHeader()
        # 根据内容自动调整宽度（最小宽度）
        header.setSectionResizeMode(ExternalScriptTableCol.enable, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ExternalScriptTableCol.path, header.ResizeMode.Stretch)
        view.setColumnWidth(ExternalScriptTableCol.name, 100)
        view.setColumnWidth(ExternalScriptTableCol.state, 200)

        # view.horizontalHeader().setStretchLastSection(True)

        # 安全的布局处理
        layout = parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(parent_widget)  # 默认使用垂直布局
            parent_widget.setLayout(layout)

        layout.addWidget(view)
        return view

    def set_config(self, config_name):
        self.config_name = config_name
        self.signal_config_update.emit()

    def load_external_scripts(self):
        self.external_scripts = self.db_manager.external_script_db.get_external_script_list_by_config(self.config_name)
        self.external_script_table_mode.beginResetModel()
        self.external_script_table_mode.external_scripts = self.external_scripts
        self.external_script_table_mode.endResetModel()

    def delete_script(self, row):
        self.external_script_table_mode.delete_script(row)

    def add_script(self):
        self.external_script_table_mode.add_script(self.config_name)

import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Any, Set, Optional

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QModelIndex, Signal, Slot
)
from PySide6.QtGui import QFont, QColor, QAction, QCursor
from PySide6.QtWidgets import (
    QApplication, QTableView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QSplitter, QGroupBox, QHeaderView,
    QStyledItemDelegate, QComboBox, QMenu, QMessageBox, QCompleter, QDialog
)

from UI.FlashCompositeControl import Ui_Form_FlashChooseFileControl
from UI.FlashConfig import Ui_FlashConfig


logger = logging.getLogger('UDSTool.' + __name__)

# ==========================================
# 1. 数据结构
# ==========================================

@dataclass
class FileConfig:
    name: str = 'Bootloader'
    default_path: str = './bin/boot.bin'
    address: str = '0x08000000'

    # 转字典
    def to_dict(self):
        return asdict(self)

    # 从字典还原
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class Step:
    step_name: str = ''
    data: bytes = b''
    external_data: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "step_name": self.step_name,
            "data": self.data.hex().upper(),  # Bytes -> Hex String
            "external_data": self.external_data
        }

    @classmethod
    def from_dict(cls, data: dict):
        # Hex String -> Bytes
        hex_str = data.get("data", "")
        byte_val = bytes.fromhex(hex_str) if hex_str else b''

        return cls(
            step_name=data.get("step_name", ""),
            data=byte_val,
            external_data=data.get("external_data", [])
        )


@dataclass
class FlashConfig:
    files: list[FileConfig] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)

    def to_json(self) -> str:
        obj_dict = {
            "files": [f.to_dict() for f in self.files],
            "steps": [s.to_dict() for s in self.steps]
        }
        return json.dumps(obj_dict, ensure_ascii=False, indent=2)

    # --- 2. 从 JSON 更新当前对象 ---
    def update_from_json(self, json_str: str):
        try:
            data = json.loads(json_str)
            self.files = [FileConfig.from_dict(f) for f in data.get("files", [])]
            self.steps = [Step.from_dict(s) for s in data.get("steps", [])]
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")
        except Exception as e:
            print(f"Error loading JSON: {e}")

    # --- 静态方法：直接从 JSON 创建新对象 ---
    @classmethod
    def from_json(cls, json_str: str):
        inst = cls()
        inst.update_from_json(json_str)
        return inst




# ==========================================
# 2. 极速代理 (Cached Delegate)
# ==========================================

class VariableSelectionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cached_items: list[str] = []

    def set_variable_list(self, items: list[str]):
        self._cached_items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)  # 允许手写输入
        editor.addItems(self._cached_items)  # 使用缓存，极速加载
        editor.completer().setCompletionMode(QCompleter.PopupCompletion)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setCurrentText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.currentText().strip()
        model.setData(index, value, Qt.EditRole)


# ==========================================
# 3. Files Model (已修复 flags)
# ==========================================

class FilesTableModel(QAbstractTableModel):
    variablesChanged = Signal()

    def __init__(self, files_list: list[FileConfig], parent=None):
        super().__init__(parent)
        self.files_list = files_list

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.files_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        item = self.files_list[index.row()]
        col = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0: return item.name
            if col == 1: return item.default_path
            if col == 2: return item.address
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if index.isValid() and role == Qt.EditRole:
            item = self.files_list[index.row()]
            col = index.column()
            val_str = str(value).strip()
            if col == 0:
                item.name = val_str
            elif col == 1:
                item.default_path = val_str
            elif col == 2:
                item.address = val_str
            self.dataChanged.emit(index, index, [role])
            if col == 0: self.variablesChanged.emit()
            return True
        return False

    # 【重要修复】添加了 flags 函数
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Name (Prefix)", "Path", "Address"][section]
        return None

    def insert_file(self):
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        self.files_list.append(FileConfig(name=f"File_{row}"))
        self.endInsertRows()
        self.variablesChanged.emit()

    def remove_file(self, row: int):
        if 0 <= row < len(self.files_list):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.files_list.pop(row)
            self.endRemoveRows()
            self.variablesChanged.emit()


# ==========================================
# 4. Steps Model (已修复 flags)
# ==========================================

class CellType(Enum):
    EMPTY = auto()
    VARIABLE = auto()
    HEX = auto()
    ERROR = auto()


class StepsTableModel(QAbstractTableModel):
    def __init__(self, steps_list: list[Step], parent=None):
        super().__init__(parent)
        self.steps_list = steps_list
        self._cached_vars_set: Set[str] = set()

    def update_variable_cache(self, var_list: list[str]):
        self._cached_vars_set = set(var_list)
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.steps_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        max_ext = max((len(s.external_data) for s in self.steps_list), default=0)
        return 2 + max_ext + 1

    def _analyze_content(self, text: str) -> CellType:
        if not text: return CellType.EMPTY
        if text in self._cached_vars_set: return CellType.VARIABLE
        if self._is_valid_hex(text): return CellType.HEX
        return CellType.ERROR

    def _is_valid_hex(self, s: str) -> bool:
        if len(s) % 2 != 0: return False
        try:
            bytes.fromhex(s)
            return True
        except ValueError:
            return False

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        row, col = index.row(), index.column()
        step = self.steps_list[row]

        text_val = ""
        if col == 0:
            text_val = step.step_name
        elif col == 1:
            text_val = step.data.hex().upper()
        elif col >= 2:
            ext_idx = col - 2
            if ext_idx < len(step.external_data):
                text_val = step.external_data[ext_idx]

        if role in (Qt.DisplayRole, Qt.EditRole):
            return text_val

        if col >= 2 and text_val:
            cell_type = self._analyze_content(text_val)
            if role == Qt.ForegroundRole:
                if cell_type == CellType.VARIABLE: return QColor("#0055AA")
                if cell_type == CellType.HEX: return QColor("#333333")
                if cell_type == CellType.ERROR: return QColor("white")
            if role == Qt.BackgroundRole:
                if cell_type == CellType.ERROR: return QColor("#D32F2F")
            if role == Qt.FontRole:
                font = QFont("Consolas", 10)
                if cell_type == CellType.VARIABLE: font.setBold(True)
                return font
            if role == Qt.ToolTipRole:
                if cell_type == CellType.VARIABLE: return "Valid Variable Reference"
                if cell_type == CellType.ERROR: return "Error: Unknown Variable or Invalid Hex"

        if role == Qt.TextAlignmentRole and col > 0:
            return Qt.AlignCenter
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False
        row, col = index.row(), index.column()
        step = self.steps_list[row]
        val_str = str(value).strip()
        old_cols = self.columnCount()

        if col == 0:
            step.step_name = val_str
        elif col == 1:
            try:
                step.data = bytes.fromhex(val_str) if val_str else b''
            except ValueError:
                return False
        else:
            ext_idx = col - 2
            if ext_idx >= len(step.external_data):
                if val_str:
                    while len(step.external_data) < ext_idx: step.external_data.append("")
                    step.external_data.append(val_str)
            else:
                step.external_data[ext_idx] = val_str

        self.dataChanged.emit(index, index, [role, Qt.ForegroundRole, Qt.BackgroundRole])
        self._cleanup_trailing_columns()
        if self.columnCount() != old_cols: self.layoutChanged.emit()
        return True

    # 【重要修复】添加了 flags 函数
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def _cleanup_trailing_columns(self):
        if not self.steps_list: return
        while True:
            max_len = max((len(s.external_data) for s in self.steps_list), default=0)
            if max_len == 0: break
            last_col_idx = max_len - 1
            is_col_empty = all(
                (last_col_idx >= len(s.external_data) or s.external_data[last_col_idx] == "") for s in self.steps_list)
            if is_col_empty:
                for s in self.steps_list:
                    if len(s.external_data) > last_col_idx: s.external_data.pop()
            else:
                break

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0: return "Step Name"
            if section == 1: return "Data (Hex)"
            return f"Param {section - 2}"
        if role == Qt.DisplayRole and orientation == Qt.Vertical: return str(section + 1)
        return None

    def insert_step(self, row: int):
        self.beginInsertRows(QModelIndex(), row, row)
        self.steps_list.insert(row, Step(step_name=f"Step_{row + 1}"))
        self.endInsertRows()

    def remove_step(self, row: int):
        if 0 <= row < len(self.steps_list):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.steps_list.pop(row)
            self.endRemoveRows()
            self._cleanup_trailing_columns()

    def remove_column(self, view_col_idx: int):
        if view_col_idx < 2: return
        ext_idx = view_col_idx - 2
        self.beginResetModel()
        for step in self.steps_list:
            if ext_idx < len(step.external_data):
                step.external_data.pop(ext_idx)
        self._cleanup_trailing_columns()
        self.endResetModel()


class FlashChooseFileControl(QWidget, Ui_Form_FlashChooseFileControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class FlashConfigPanel(Ui_FlashConfig, QDialog):
    def __init__(self, flash_config: Optional[FlashConfig], parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.base_vars = {}
        self.config = flash_config if flash_config else FlashConfig()


        self.file_model = FilesTableModel(self.config.files)
        self.file_view = self._add_file_view(self.groupBox_files, self.file_model)

        self.pushButton_AddFile.clicked.connect(self.file_model.insert_file)
        self.pushButton_RemoveFile.clicked.connect(self._remove_current_file)

        # self.file_view = QTableView()
        # self.file_view.setModel(self.file_model)
        # self.file_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.file_view.setSelectionBehavior(QTableView.SelectRows)


        self.step_model = StepsTableModel(self.config.steps)
        self.var_delegate = VariableSelectionDelegate(self)
        self.step_view = self._add_steps_view(self.groupBox_steps, self.step_model, self.var_delegate)
        # self.step_view = QTableView()
        # self.step_view.setModel(self.step_model)
        # self.step_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.step_view.customContextMenuRequested.connect(self._show_context_menu)
        self.file_model.variablesChanged.connect(self.refresh_global_cache)
        self.refresh_global_cache()

    def _remove_current_file(self):
        idx = self.file_view.currentIndex()
        if idx.isValid(): self.file_model.remove_file(idx.row())

    def refresh_global_cache(self):
        vars_ = list(self.base_vars.keys())
        for f in self.config.files:
            if f.name:
                vars_.extend([f"{f.name}_addr", f"{f.name}_size", f"{f.name}_crc"])
        vars_.sort()
        self.step_model.update_variable_cache(vars_)
        self.var_delegate.set_variable_list(vars_)

    def _show_context_menu(self, pos):
        menu = QMenu()
        idx = self.step_view.indexAt(pos)
        act_add = QAction("Add Step Below", self)
        act_add.triggered.connect(
            lambda: self.step_model.insert_step(idx.row() + 1 if idx.isValid() else self.step_model.rowCount()))
        menu.addAction(act_add)
        if idx.isValid():
            act_del = QAction("Delete Step", self)
            act_del.triggered.connect(lambda: self.step_model.remove_step(idx.row()))
            menu.addAction(act_del)
            if idx.column() >= 2:
                menu.addSeparator()
                act_col = QAction("Delete This Column", self)
                act_col.triggered.connect(lambda: self.step_model.remove_column(idx.column()))
                menu.addAction(act_col)
        menu.exec(QCursor.pos())


    def _add_file_view(self, parent_widget, mode):
        """
        在指定控件上添加控件file_view
        :param parent_widget: 父控件
        """
        if not parent_widget:
            logger.error("父控件无效")
            return
        file_view = QTableView()
        file_view.setModel(mode)
        logger.debug(f"父控件：{parent_widget.objectName()}")


        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(file_view)
        layout.setStretchFactor(file_view, 1)

        return file_view

    def _add_steps_view(self, parent_widget, mode, delegate):
        """
        在指定控件上添加控件steps_view
        :param parent_widget: 父控件
        """
        if not parent_widget:
            logger.error("父控件无效")
            return
        steps_view = QTableView()
        steps_view.setModel(mode)
        steps_view.setContextMenuPolicy(Qt.CustomContextMenu)
        for i in range(2, 256):
            steps_view.setItemDelegateForColumn(i, delegate)
        logger.debug(f"父控件：{parent_widget.objectName()}")


        # 获取或创建布局
        layout = parent_widget.layout()
        if layout is None:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 添加表格并设置拉伸因子（核心：让表格铺满）
        layout.addWidget(steps_view)
        layout.setStretchFactor(steps_view, 1)

        return steps_view



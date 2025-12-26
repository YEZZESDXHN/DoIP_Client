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
from global_variables import gFlashVars

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


class VariableSelectionDelegate(QStyledItemDelegate):
    """
    极简 Delegate：不存储任何数据，创建编辑器时直接问 Model 要数据。
    """

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)

        # [优化关键] 直接从 Model 获取当前最新的变量列表
        # 只要 Model 更新了，这里打开必然是新的，无需手动同步
        if hasattr(index.model(), 'get_variable_list'):
            editor.addItems(index.model().get_variable_list())

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
# 3. Files Model
# ==========================================
class FilesTableModel(QAbstractTableModel):
    variablesChanged = Signal()  # 通知外部变量可能变了

    def __init__(self, files_list: list[FileConfig], parent=None):
        super().__init__(parent)
        self.files_list = files_list

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.files_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 3

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        item = self.files_list[index.row()]
        col = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return [item.name, item.default_path, item.address][col]
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if index.isValid() and role == Qt.EditRole:
            item = self.files_list[index.row()]
            col = index.column()
            val_str = str(value).strip()

            if col == 0:  # Name changed
                if item.name != val_str:
                    item.name = self._get_unique_name(val_str, index.row())
                    self.variablesChanged.emit()  # 只有名字改了才影响变量列表
            elif col == 1:
                item.default_path = val_str
            elif col == 2:
                item.address = val_str

            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def insert_file(self):
        row = self.rowCount()
        base_name = f"File_{row+1}"

        # 核心修改：在插入前调用查重逻辑
        # 传入 -1 作为 exclude_row，表示与列表中所有现有项进行对比
        unique_name = self._get_unique_name(base_name, -1)

        self.beginInsertRows(QModelIndex(), row, row)
        self.files_list.append(FileConfig(name=unique_name))
        self.endInsertRows()

        self.variablesChanged.emit()

    def remove_file(self, row: int):
        if 0 <= row < len(self.files_list):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.files_list.pop(row)
            self.endRemoveRows()
            self.variablesChanged.emit()

    def _get_unique_name(self, base_name: str, exclude_row: int) -> str:
        existing = {f.name for i, f in enumerate(self.files_list) if i != exclude_row}
        if base_name not in existing: return base_name
        counter = 1
        while f"{base_name}_{counter}" in existing: counter += 1
        return f"{base_name}_{counter}"

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Name (Prefix)", "Path", "Address"][section]
        return None


# ==========================================
# 4. Steps Model (核心优化)
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
        # [优化关键] 内部持有变量缓存
        self._valid_vars_set: Set[str] = set()  # O(1) 查找，用于高亮
        self._valid_vars_list: list[str] = []  # 有序列表，用于 Delegate 下拉

    def update_context(self, all_vars: list[str]):
        """
        接收最新的变量列表，更新内部缓存并刷新视图
        """
        self._valid_vars_list = sorted(all_vars)
        self._valid_vars_set = set(all_vars)
        # 强制刷新整个视图，因为所有单元格的颜色可能都需要重新计算
        self.beginResetModel()
        self.endResetModel()

    def get_variable_list(self) -> list[str]:
        """供 Delegate 调用"""
        return self._valid_vars_list

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.steps_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        max_ext = max((len(s.external_data) for s in self.steps_list), default=0)
        return 2 + max_ext + 1

    def _analyze_content(self, text: str) -> CellType:
        if not text: return CellType.EMPTY
        if text in self._valid_vars_set: return CellType.VARIABLE  # O(1) 极速查找
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

        # 获取文本数据
        text_val = ""
        if col == 0:
            text_val = step.step_name
        elif col == 1:
            text_val = step.data.hex().upper()
        elif col >= 2:
            ext_idx = col - 2
            if ext_idx < len(step.external_data): text_val = step.external_data[ext_idx]

        if role in (Qt.DisplayRole, Qt.EditRole): return text_val

        # 样式处理
        if col >= 2 and text_val:
            cell_type = self._analyze_content(text_val)
            if role == Qt.ForegroundRole:
                return {
                    CellType.VARIABLE: QColor("#0055AA"),
                    CellType.HEX: QColor("#333333"),
                    CellType.ERROR: QColor("white")
                }.get(cell_type)
            if role == Qt.BackgroundRole and cell_type == CellType.ERROR:
                return QColor("#D32F2F")
            if role == Qt.FontRole and cell_type == CellType.VARIABLE:
                font = QFont("Consolas", 10)
                font.setBold(True)
                return font

        if role == Qt.TextAlignmentRole and col > 0: return Qt.AlignCenter
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False
        row, col = index.row(), index.column()
        step = self.steps_list[row]
        val_str = str(value).strip()

        # 记录旧列数以便判断布局是否变化
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
            # 自动扩展 list
            if ext_idx >= len(step.external_data):
                if val_str:
                    step.external_data.extend([""] * (ext_idx - len(step.external_data)))
                    step.external_data.append(val_str)
            else:
                step.external_data[ext_idx] = val_str

        self.dataChanged.emit(index, index, [role, Qt.ForegroundRole, Qt.BackgroundRole])

        # 清理空列
        self._cleanup_trailing_columns()
        if self.columnCount() != old_cols: self.layoutChanged.emit()
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def _cleanup_trailing_columns(self):
        if not self.steps_list: return
        while True:
            max_len = max((len(s.external_data) for s in self.steps_list), default=0)
            if max_len == 0: break
            # 检查最后一列是否全空
            is_col_empty = all((i >= len(s.external_data) or s.external_data[i] == "")
                               for s in self.steps_list for i in [max_len - 1])
            if is_col_empty:
                for s in self.steps_list:
                    if len(s.external_data) == max_len: s.external_data.pop()
            else:
                break

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0: return "Step Name"
            if section == 1: return "Data (Hex)"
            return f"Param {section - 2}"
        if role == Qt.DisplayRole and orientation == Qt.Vertical: return str(section + 1)
        return None

    # 辅助增删方法
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

class FlashConfigPanel(Ui_FlashConfig, QDialog):
    def __init__(self, flash_config: Optional[FlashConfig], parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 1. 初始化配置和全局变量引用
        self.config = flash_config if flash_config else FlashConfig()
        self.global_vars_ref = gFlashVars  # 持有引用，如果需要修改它

        # 2. 初始化 Model
        self.file_model = FilesTableModel(self.config.files)
        self.step_model = StepsTableModel(self.config.steps)

        # 3. 初始化 Views
        self.file_view = self._setup_view(self.groupBox_files, self.file_model)

        # Delegate 不需要再传递 self，也不需要手动 set_variable_list
        self.var_delegate = VariableSelectionDelegate()
        self.step_view = self._setup_view(self.groupBox_steps, self.step_model, self.var_delegate)

        # 4. 信号连接
        self.pushButton_AddFile.clicked.connect(self.file_model.insert_file)
        self.pushButton_RemoveFile.clicked.connect(self._remove_current_file)
        self.step_view.customContextMenuRequested.connect(self._show_context_menu)

        # [关键] 当文件列表的名字改变时，重新计算所有可用变量
        self.file_model.variablesChanged.connect(self.recalculate_variables)

        # 5. 初始计算
        self.recalculate_variables()

    def recalculate_variables(self):
        """
        核心逻辑：汇总全局变量 + 文件变量，分发给需要的地方
        """
        # 1. 获取全局基础变量 (Keys)
        self.global_vars_ref.clear()
        all_vars = list(self.global_vars_ref.keys())

        # 2. 获取文件动态变量并添加到列表
        # 如果你想修改全局 gFlashVars，可以在这里进行 update，但通常建议只在需要执行时做
        # 这里我们只负责收集所有可用变量名给 UI 显示
        for f in self.config.files:
            if f.name:
                # 按照约定生成变量名
                all_vars.extend([f"{f.name}_addr", f"{f.name}_size", f"{f.name}_crc"])
                for var in all_vars:
                    self.global_vars_ref[var] = None

        # 3. 更新 StepModel 的上下文
        self.step_model.update_context(all_vars)

    def _remove_current_file(self):
        idx = self.file_view.currentIndex()
        if idx.isValid(): self.file_model.remove_file(idx.row())

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
                act_col = QAction("Delete Column", self)
                act_col.triggered.connect(lambda: self.step_model.remove_column(idx.column()))
                menu.addAction(act_col)
        menu.exec(QCursor.pos())

    def _setup_view(self, parent_widget, model, delegate=None):
        view = QTableView()
        view.setModel(model)
        view.setContextMenuPolicy(Qt.CustomContextMenu)

        # 自动应用 Delegate 到参数列 (从第2列开始)
        if delegate:
            # 一般设个足够大的范围或者重写 view 的 itemDelegateForIndex
            for i in range(2, 100):
                view.setItemDelegateForColumn(i, delegate)

        layout = parent_widget.layout()
        if not layout:
            layout = QHBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(view)
        return view


class FlashChooseFileControl(QWidget, Ui_Form_FlashChooseFileControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum, auto, IntEnum
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


# 定义文件的列
class FileCol(IntEnum):
    NAME = 0
    PATH = 1
    ADDRESS = 2


# 定义步骤的列
class StepCol(IntEnum):
    NAME = 0
    DATA = 1
    PARAMS_START = 2  # 参数起始列

class VariableSelectionDelegate(QStyledItemDelegate):
    """
    极简 Delegate：不存储任何数据，创建编辑器时直接问 Model 要数据。
    """

    def createEditor(self, parent, option, index):
        # [优化]：逻辑内聚，Delegate 自己判断只处理参数列
        # 假设 StepModel 在这里，如果用于 FileModel 则可能需要调整，或者传入 filter
        if index.column() < StepCol.PARAMS_START:
            return super().createEditor(parent, option, index)

        editor = QComboBox(parent)
        editor.setEditable(True)

        # 鸭子类型检查：如果 Model 有这个方法就调用
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
            # [优化] 使用 match 或 if-elif 配合枚举，清晰易读
            if col == FileCol.NAME: return item.name
            if col == FileCol.PATH: return item.default_path
            if col == FileCol.ADDRESS: return item.address
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False

        item = self.files_list[index.row()]
        col = index.column()
        val_str = str(value).strip()

        if col == FileCol.NAME:
            if item.name != val_str:
                # 查重逻辑保持不变
                item.name = self._get_unique_name(val_str, index.row())
                self.variablesChanged.emit()
        elif col == FileCol.PATH:
            item.default_path = val_str
        elif col == FileCol.ADDRESS:
            item.address = val_str

        self.dataChanged.emit(index, index, [role])
        return True

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
        # [优化] 基础列数 + 最大参数列数
        max_ext = max((len(s.external_data) for s in self.steps_list), default=0)
        return StepCol.PARAMS_START + max_ext + 1

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

        # [优化] 数据获取逻辑
        text_val = ""
        if col == StepCol.NAME:
            text_val = step.step_name
        elif col == StepCol.DATA:
            text_val = step.data.hex().upper()
        elif col >= StepCol.PARAMS_START:
            ext_idx = col - StepCol.PARAMS_START
            if ext_idx < len(step.external_data):
                text_val = step.external_data[ext_idx]

        # 样式处理逻辑保持不变，但建议将 CellType 判断逻辑提取为单独的方法
        if role == Qt.ForegroundRole and col >= StepCol.PARAMS_START and text_val:
            return self._get_color_for_value(text_val)  # 封装颜色逻辑

        if role in (Qt.DisplayRole, Qt.EditRole): return text_val
        if role == Qt.TextAlignmentRole and col > 0: return Qt.AlignCenter
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False
        row, col = index.row(), index.column()
        step = self.steps_list[row]
        val_str = str(value).strip()

        old_cols = self.columnCount()  # 记录旧列数

        if col == StepCol.NAME:
            step.step_name = val_str
        elif col == StepCol.DATA:
            try:
                step.data = bytes.fromhex(val_str) if val_str else b''
            except ValueError:
                return False
        elif col >= StepCol.PARAMS_START:
            # [优化] 封装动态列表扩展逻辑
            self._set_external_data(step, col - StepCol.PARAMS_START, val_str)

        self.dataChanged.emit(index, index, [role, Qt.ForegroundRole, Qt.BackgroundRole])

        self._cleanup_trailing_columns()
        if self.columnCount() != old_cols:
            self.layoutChanged.emit()  # 列数变了必须发这个，否则视图不刷新
        return True

    def _set_external_data(self, step: Step, ext_idx: int, value: str):
        """Helper to safely set list data, extending if necessary."""
        current_len = len(step.external_data)
        if ext_idx < current_len:
            step.external_data[ext_idx] = value
        else:
            # 补齐中间的空位
            if value:  # 只有值不为空时才扩展
                step.external_data.extend([""] * (ext_idx - current_len))
                step.external_data.append(value)

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

        # 1. 初始化数据副本 (避免直接操作原始对象，直到点击 OK)
        # 建议：这里最好深拷贝 flash_config，防止 Cancel 后数据也被改了
        # self.config = copy.deepcopy(flash_config) if flash_config else FlashConfig()
        self.config = flash_config if flash_config else FlashConfig()

        # 2. 初始化 Model
        self.file_model = FilesTableModel(self.config.files)
        self.step_model = StepsTableModel(self.config.steps)

        # 3. 初始化 Views
        # 直接传入占位符 widget，内部自动处理布局
        self.file_view = self._setup_view(self.groupBox_files, self.file_model)

        # [优化] 设置全局 Delegate，Delegate 内部会智能判断列
        self.step_view = self._setup_view(self.groupBox_steps, self.step_model)
        self.step_view.setItemDelegate(VariableSelectionDelegate(self.step_view))

        # 4. 信号连接
        self.pushButton_AddFile.clicked.connect(self.file_model.insert_file)
        self.pushButton_RemoveFile.clicked.connect(self._remove_current_file)

        # 上下文菜单
        self.step_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.step_view.customContextMenuRequested.connect(self._show_context_menu)

        # [关键] 变量联动
        # 只有当文件列表变更时，才触发变量列表的重新计算
        self.file_model.variablesChanged.connect(self.recalculate_variables)

        # 5. 初始计算
        self.recalculate_variables()

    def recalculate_variables(self):
        """
        [核心优化]：纯计算逻辑，不产生副作用。
        只负责生成变量名列表给 UI 使用，不修改全局 gFlashVars。
        """
        # 1. 基础变量 (通常是固定的或从系统读取)
        # 不要直接引用全局 gFlashVars，而是应该拷贝一份 keys 或者硬编码基础变量
        # 假设这里有一些系统预设变量：
        current_vars = ["Global_Time", "Sys_Version"]

        # 2. 动态追加文件相关的变量
        for f in self.config.files:
            if f.name:
                safe_name = f.name.strip()
                current_vars.extend([
                    f"{safe_name}_addr",
                    f"{safe_name}_size",
                    f"{safe_name}_crc"
                ])

        # 3. 仅更新 UI 上下文 (StepModel)
        # StepModel 拿到这个列表后，负责更新高亮和下拉提示
        self.step_model.update_context(current_vars)

    def _setup_view(self, parent_widget, model):
        """通用视图设置"""
        view = QTableView()
        view.setModel(model)

        # 常用视图设置
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QTableView.SelectRows)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        view.horizontalHeader().setStretchLastSection(True)

        # 安全的布局处理
        layout = parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(parent_widget)  # 默认使用垂直布局
            parent_widget.setLayout(layout)

        layout.addWidget(view)
        return view

    def _remove_current_file(self):
        idx = self.file_view.currentIndex()
        if idx.isValid():
            self.file_model.remove_file(idx.row())

    def _show_context_menu(self, pos):
        menu = QMenu()
        idx = self.step_view.indexAt(pos)

        # 无论是否选中，都可以添加
        act_add = QAction("Insert Step Below", self)
        row_to_add = idx.row() + 1 if idx.isValid() else self.step_model.rowCount()
        act_add.triggered.connect(lambda: self.step_model.insert_step(row_to_add))
        menu.addAction(act_add)

        if idx.isValid():
            act_del = QAction("Delete Step", self)
            act_del.triggered.connect(lambda: self.step_model.remove_step(idx.row()))
            menu.addAction(act_del)

            # [优化] 使用枚举判断列
            if idx.column() >= StepCol.PARAMS_START:
                menu.addSeparator()
                act_col = QAction("Delete Column", self)
                act_col.triggered.connect(lambda: self.step_model.remove_column(idx.column()))
                menu.addAction(act_col)

        menu.exec(QCursor.pos())

    def accept(self):
        """
        [新增] 点击 OK 时才真正更新全局变量
        """
        # 可以在这里做最终的数据校验
        # 也可以在这里把 self.config 同步回 gFlashVars (如果确实需要的话)

        # 示例：更新全局变量字典 (副作用只发生在最后一步)
        gFlashVars.clear()
        for var in self.step_model.get_variable_list():
            gFlashVars[var] = None

        super().accept()


class FlashChooseFileControl(QWidget, Ui_Form_FlashChooseFileControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
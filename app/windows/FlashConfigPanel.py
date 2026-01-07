import copy
import logging
import os
import re
from enum import Enum, auto, IntEnum
from typing import Any, Set, Optional, List

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QModelIndex, Signal
)
from PySide6.QtGui import QColor, QAction, QCursor, QPalette, QMouseEvent, QContextMenuEvent
from PySide6.QtWidgets import (
    QTableView, QVBoxLayout, QWidget, QHeaderView,
    QStyledItemDelegate, QComboBox, QMenu, QCompleter, QDialog, QStyleOptionViewItem, QLineEdit, QFileDialog,
    QAbstractItemView
)
from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator

from app.core.ChecksumStrategy import ChecksumType
from app.global_variables import gFlashVars, FlashFileVars
from app.resources.resources import IconEngine
from app.ui.FlashCompositeControl import Ui_Form_FlashChooseFileControl
from app.ui.FlashConfig import Ui_FlashConfig

logger = logging.getLogger('UDSTool.' + __name__)

# ==========================================
# 1. 数据结构
# ==========================================

flash_file_block_var_suffix = ['data', 'addr', 'size', 'checksum']


# @dataclass
class FileConfig(BaseModel):
    name: str = ''
    default_path: str = ''
    address: str = ''


# @dataclass
class Step(BaseModel):
    step_name: str = ''
    is_call: bool = False
    data: bytes = b''
    exp_resp_data: bytes = b''
    external_data: list[str] = Field(default_factory=list)

    @field_serializer('data')
    def serialize_data(self, data: bytes, _info):
        return data.hex().upper()

    @field_validator('data', mode='before')
    @classmethod
    def validate_data(cls, v):
        # Pydantic 在校验类型前会先运行这个函数
        # v 就是从 JSON 里拿到的那个字符串，比如 "FF00"
        if isinstance(v, str):
            try:
                # 将 Hex 字符串转回二进制
                return bytes.fromhex(v)
            except ValueError:
                # 如果字符串不是合法的 Hex，可以选择报错或返回空
                raise ValueError("数据格式错误: 必须是有效的 Hex 字符串")
        return v


# @dataclass
class TransmissionParameters(BaseModel):
    checksum_type: ChecksumType = ChecksumType.crc32
    data_format_identifier: int = 0
    max_number_of_block_length: Optional[int] = None
    memory_address_parameter_length: int = 4
    memory_size_parameter_length: int = 4


# @dataclass
class FlashConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    transmission_parameters: TransmissionParameters = Field(default_factory=TransmissionParameters)
    files: list[FileConfig] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()

    # # --- 2. 从 JSON 更新当前对象 ---
    # def update_from_json(self, json_str: str):
    #     try:
    #         data = json.loads(json_str)
    #         tp_data = data.get("transmission_parameters")
    #         if tp_data:
    #             self.transmission_parameters = TransmissionParameters.from_dict(tp_data)
    #         self.files = [FileConfig.from_dict(f) for f in data.get("files", [])]
    #         self.steps = [Step.from_dict(s) for s in data.get("steps", [])]
    #     except json.JSONDecodeError:
    #         print("Error: Invalid JSON string")
    #     except Exception as e:
    #         print(f"Error loading JSON: {e}")

    @classmethod
    def from_json(cls, json_str: str):
        return cls.model_validate_json(json_str)


# 定义文件的列
class FileCol(IntEnum):
    NAME = 0
    PATH = 1
    ADDRESS = 2


# 定义步骤的列
class StepCol(IntEnum):
    NAME = 0
    REQ_DATA = 1
    EXP_RESP_DATA = 2
    PARAMS_START = 3  # 参数起始列


class FlashStepCall(Enum):
    wait = "Wait"


STEP_CALL_VALUES = tuple(item.value for item in FlashStepCall)


class VariableSelectionDelegate(QStyledItemDelegate):
    """
    极简 Delegate：不存储任何数据，创建编辑器时直接问 Model 要数据。
    """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        # 1. 先让父类完成基础初始化（字体、对齐、默认颜色等）
        super().initStyleOption(option, index)

        # 2. 获取 Model 中定义的颜色 (即你在 data 方法中返回的 ForegroundRole)
        foreground_color = index.data(Qt.ForegroundRole)

        if foreground_color and isinstance(foreground_color, QColor):
            # [核心修复]
            # 强制将 "选中状态下的文字颜色" (HighlightedText) 设置为与 "普通文字颜色" 一致
            # 这样即使单元格被选中，颜色也不会变成白色，而是保持你定义的红/蓝/灰
            option.palette.setColor(QPalette.HighlightedText, foreground_color)

            # 同时也确保普通文本颜色正确（通常父类已经处理，但为了保险）
            option.palette.setColor(QPalette.Text, foreground_color)

    def createEditor(self, parent, option, index):
        # [优化]：逻辑内聚，Delegate 自己判断只处理参数列
        # 假设 StepModel 在这里，如果用于 FileModel 则可能需要调整，或者传入 filter
        if index.column() == StepCol.NAME:
            editor = QComboBox(parent)
            editor.setEditable(True)
            editor.addItems([item.value for item in FlashStepCall])
            return editor
        elif index.column() < StepCol.PARAMS_START:
            return super().createEditor(parent, option, index)
        else:
            model = index.model()
            if not isinstance(model, StepsTableModel):
                return super().createEditor(parent, option, index)
            row = index.row()
            if model.steps_list[row].is_call:
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
        if value and isinstance(editor, QComboBox):
            editor.setCurrentText(str(value))
        elif value and isinstance(editor, QLineEdit):
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.currentText()
            model.setData(index, value, Qt.EditRole)
        elif isinstance(editor, QLineEdit):
            value = editor.text()
            model.setData(index, value, Qt.EditRole)


class FilesTableView(QTableView):
    """自定义表格视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 默认规则：双击/选中后单击 均可编辑
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

    def mousePressEvent(self, event: QMouseEvent):
        """单击Path列单元格弹出文件选择框，其他列保留默认编辑逻辑"""
        index = self.indexAt(event.pos())

        # 仅拦截 Path 列的左键单击事件
        if index.isValid() and index.column() == FileCol.PATH and event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog(index)
            return  # 阻止Path列触发默认的"选中单击编辑"

        # 其他列/情况执行默认逻辑（保留编辑能力）
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """仅拦截Path列的双击事件，其他列保留默认双击编辑"""
        index = self.indexAt(event.pos())

        if index.isValid() and index.column() == FileCol.PATH and event.button() == Qt.MouseButton.LeftButton:
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
        if index.column() == FileCol.PATH:
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
            "Hex (*.hex);;bin (*.bin);;S19 (*.s19);;All Files (*)"
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


class FilesTableModel(QAbstractTableModel):
    variablesChanged = Signal()  # 通知外部变量可能变了

    def __init__(self, files_list: List[FileConfig], parent=None):
        super().__init__(parent)
        self.files_list = files_list

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.files_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 3

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid(): return None
        item = self.files_list[index.row()]
        col = index.column()

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == FileCol.NAME:
                return item.name
            if col == FileCol.PATH:
                return item.default_path
            if col == FileCol.ADDRESS:
                return item.address
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole: return False

        item = self.files_list[index.row()]
        col = index.column()
        val_str = str(value).strip()

        if col == FileCol.NAME:
            if item.name != val_str:
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

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ["Name (Prefix)", "Path", "Address(Hex)"][section]


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
        # 预编译正则：匹配 "任意字符[数字]" 的格式
        # ^(.+)  : 捕获组1，变量名 (例如 app_crc)
        # \[     : 匹配左方括号
        # \d+    : 匹配里面的数字索引 (如果索引可能是变量，可用 .+ 代替 \d+)
        # \]     : 匹配右方括号
        self._array_pattern = re.compile(r'^(.+)\[(\d+)\]$')

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

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        row, col = index.row(), index.column()
        step = self.steps_list[row]

        # [优化] 数据获取逻辑
        text_val = ""
        if col == StepCol.NAME:
            text_val = step.step_name
        elif col == StepCol.REQ_DATA:
            text_val = step.data.hex().upper()
        elif col == StepCol.EXP_RESP_DATA:
            text_val = step.exp_resp_data.hex().upper()
        elif col >= StepCol.PARAMS_START:
            ext_idx = col - StepCol.PARAMS_START
            if ext_idx < len(step.external_data):
                text_val = step.external_data[ext_idx]

        if role == Qt.ItemDataRole.ForegroundRole and col == StepCol.NAME and text_val:
            if self.is_step_call(text_val):
                return QColor("#0055AA")  # 蓝色
            else:
                return QColor("#000000")  # 蓝色

        # 样式处理逻辑保持不变，但建议将 CellType 判断逻辑提取为单独的方法
        if role == Qt.ItemDataRole.ForegroundRole and col >= StepCol.PARAMS_START and text_val:
            return self._get_color_for_value(step.is_call, text_val)  # 封装颜色逻辑

        if role in (Qt.DisplayRole, Qt.EditRole):
            return text_val
        if role == Qt.TextAlignmentRole and col > 0:
            return Qt.AlignCenter
        return None


    def is_step_call(self, text: str) -> bool:
        if not text:
            return False  # 使用默认颜色
        if text in STEP_CALL_VALUES:
            return True
        else:
            return False


    def _get_color_for_value(self, is_step_call, text: str) -> QColor:
        """
        根据文本内容返回对应的字体颜色
        1. 变量名 (精确匹配 或 数组模式) -> 蓝色
        2. 合法Hex -> 黑色/深灰
        3. 非法内容 -> 红色
        """
        if not text:
            return None  # 使用默认颜色

        if is_step_call:
            return None
        if '[' in text:
            # 尝试用正则解析 "name[index]"
            match = self._array_pattern.match(text)
            if match:
                name_part = match.group(1)
                # 构造定义中的 key 格式: "name[]"
                array_def_key = f"{name_part}[]"

                # 只有当对应的 "name[]" 存在于集合中时，才算合法
                if array_def_key in self._valid_vars_set:
                    return QColor("#0055AA")  # 蓝色

            # --- 分支 2: 文本不包含 '[' -> 视为普通标量用法尝试 ---
        else:
            # 只有当 text 精确存在于集合中（且集合里存的不是带[]的版本）才算合法
            # 因为我们已经排除了含 '[' 的情况，所以这里不会匹配到 "app_crc[]"
            if text in self._valid_vars_set:
                return QColor("#0055AA")  # 蓝色

            # --- 逻辑 C: Hex 检查 (如果上面没返回，说明不是变量) ---
        if self._is_valid_hex(text):
            return QColor("#333333")  # 深灰/黑

            # --- 逻辑 D: 错误 (既不是合法变量，也不是Hex) ---
        return QColor("#D32F2F")  # 红色

    def _is_valid_hex(self, s: str) -> bool:
        """辅助函数：判断字符串是否为合法的 Hex"""
        # 长度必须是偶数 (比如 "AA" 是对的, "A" 是错的)
        if len(s) % 2 != 0:
            return False
        try:
            bytes.fromhex(s)
            return True
        except ValueError:
            return False

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False
        row, col = index.row(), index.column()
        step = self.steps_list[row]
        val_str = str(value).strip()

        old_cols = self.columnCount()  # 记录旧列数

        if col == StepCol.NAME:
            step.step_name = val_str
            if self.is_step_call(val_str):
                step.is_call = True
            else:
                step.is_call = False
        elif col == StepCol.REQ_DATA:
            try:
                step.data = bytes.fromhex(val_str) if val_str else b''
            except ValueError:
                return False
        elif col == StepCol.EXP_RESP_DATA:
            try:
                step.exp_resp_data = bytes.fromhex(val_str) if val_str else b''
            except ValueError:
                return False
        elif col >= StepCol.PARAMS_START:
            # [优化] 封装动态列表扩展逻辑
            self._set_external_data(step, col - StepCol.PARAMS_START, val_str)

        roles_changed = [Qt.EditRole, Qt.DisplayRole, Qt.ForegroundRole]
        self.dataChanged.emit(index, index, roles_changed)

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
            if section == StepCol.NAME:
                return "Step Name"
            elif section == StepCol.REQ_DATA:
                return "Req Data (Hex)"
            elif section == StepCol.EXP_RESP_DATA:
                return "Exp Resp Data (Hex)"
            else:
                return f"Param {section - 2}"
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return str(section + 1)
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
        self.setWindowIcon(IconEngine.get_icon('config'))
        self.setWindowTitle("Flash Config")

        # 1. 初始化数据副本 (避免直接操作原始对象，直到点击 OK)
        # 建议：这里最好深拷贝 flash_config，防止 Cancel 后数据也被改了
        self.config = copy.deepcopy(flash_config) if flash_config else FlashConfig()
        # self.config = flash_config if flash_config else FlashConfig()
        self.init_ui()
        # 2. 初始化 Model
        self.file_model = FilesTableModel(self.config.files)
        self.step_model = StepsTableModel(self.config.steps)

        # 3. 初始化 Views
        # 直接传入占位符 widget，内部自动处理布局
        self.file_view = self._setup_view(self.groupBox_files, self.file_model, FilesTableView())
        self.file_view.setColumnWidth(FileCol.PATH, 300)

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

    def init_ui(self):
        self.comboBox_Checksum.clear()

        # 2. 遍历枚举并添加
        for checksum in ChecksumType:
            # addItem 接受字符串
            self.comboBox_Checksum.addItem(checksum)
        transmission_parameters = self.config.transmission_parameters
        index = self.comboBox_Checksum.findText(transmission_parameters.checksum_type.value)
        if index >= 0:
            self.comboBox_Checksum.setCurrentIndex(index)
        else:
            self.comboBox_Checksum.setCurrentIndex(0)

        self.lineEdit_dataFormatIdentifier.setText(str(transmission_parameters.data_format_identifier))

        index = self.comboBox_MemoryAddressParameterLength.findText(str(transmission_parameters.memory_address_parameter_length))
        if index >= 0:
            self.comboBox_MemoryAddressParameterLength.setCurrentIndex(index)
        else:
            self.comboBox_MemoryAddressParameterLength.setCurrentIndex(0)

        index = self.comboBox_MemorySizeParameterLength.findText(
            str(transmission_parameters.memory_size_parameter_length))
        if index >= 0:
            self.comboBox_MemorySizeParameterLength.setCurrentIndex(index)
        else:
            self.comboBox_MemorySizeParameterLength.setCurrentIndex(0)

        try:
            max_number_of_block_length_hex = hex(transmission_parameters.max_number_of_block_length).lower()
            index = self.comboBox_MaxNumberOfBlockLength.findText(
                max_number_of_block_length_hex)

        except:
            index = 0
        if index >= 0:
            self.comboBox_MaxNumberOfBlockLength.setCurrentIndex(index)
        else:
            self.comboBox_MaxNumberOfBlockLength.setCurrentIndex(0)

    def recalculate_variables(self):
        """
        [核心优化]：纯计算逻辑，不产生副作用。
        只负责生成变量名列表给 UI 使用，不修改全局 gFlashVars。
        """
        # 1. 基础变量 (通常是固定的或从系统读取)
        # 不要直接引用全局 gFlashVars，而是应该拷贝一份 keys 或者硬编码基础变量
        # 假设这里有一些系统预设变量：
        current_vars = []
        # 2. 动态追加文件相关的变量
        for f in self.config.files:
            if f.name:
                safe_name = f.name.strip()
                ext_list = []
                for item in flash_file_block_var_suffix:
                    ext_list.append(f"{safe_name}_{item}[]")
                for item in flash_file_block_var_suffix:
                    ext_list.append(f"{safe_name}_{item}")
                current_vars.extend(ext_list)

        # 3. 仅更新 UI 上下文 (StepModel)
        # StepModel 拿到这个列表后，负责更新高亮和下拉提示
        self.step_model.update_context(current_vars)

    def _setup_view(self, parent_widget, model, view=None):
        """通用视图设置"""
        if not view:
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
        gFlashVars.files_vars.clear()
        for var in self.file_model.files_list:
            gFlashVars.files_vars[var.name] = FlashFileVars()

        self.config.transmission_parameters.memory_address_parameter_length = int(self.comboBox_MemoryAddressParameterLength.currentText())
        self.config.transmission_parameters.memory_size_parameter_length = int(self.comboBox_MemorySizeParameterLength.currentText())
        try:
            self.config.transmission_parameters.max_number_of_block_length = int(self.comboBox_MaxNumberOfBlockLength.currentText(), 16)
        except:
            self.config.transmission_parameters.max_number_of_block_length = None
        self.config.transmission_parameters.data_format_identifier = int(self.lineEdit_dataFormatIdentifier.text(), 16)
        self.config.transmission_parameters.checksum_type = ChecksumType(self.comboBox_Checksum.currentText())

        super().accept()


class FlashChooseFileControl(QWidget, Ui_Form_FlashChooseFileControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

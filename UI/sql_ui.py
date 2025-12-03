import logging
import sqlite3
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QDialog, QMessageBox, QHeaderView,
                               QAbstractItemView)
from PySide6.QtCore import Qt, QSortFilterProxyModel

from UI.sql_table_ui import Ui_sql

logger = logging.getLogger("UiCustom")


class SQLTablePanel(Ui_sql, QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_table = None
        self.setWindowTitle(f'SQL可视化面板 - {database}')

        self.setupUi(self)
        self.init_table_settings()
        self.init_model()
        self.bind_events()
        self.load_all_tables()
        # if self.current_table:
        #     self.load_table_data(self.current_table)

    def init_table_settings(self):
        """初始化表格样式和功能"""
        self.tableView.setSortingEnabled(True)
        # self.tableView.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.ResizeMode.ResizeToContents
        # )
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

    def init_model(self):
        """初始化数据模型（优化筛选配置）"""
        self.source_model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        self.proxy_model.setFilterKeyColumn(-1)  # 筛选所有列
        self.tableView.setModel(self.proxy_model)

    def bind_events(self):
        """绑定事件（确保稳定）"""
        self.comboBox_table.currentTextChanged.connect(self.switch_table)
        self.btn_refresh.clicked.connect(self.refresh_current_table)

        # 筛选输入框事件
        self.lineEdit_filter.textChanged.connect(self.filter_data)
        self.lineEdit_filter.setPlaceholderText("输入关键词筛选（如：张、男、25）")

    def load_all_tables(self):
        """加载表列表"""
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [table[0] for table in cursor.fetchall()]

                if not tables:
                    QMessageBox.warning(self, "提示", "数据库中没有找到用户表！")
                    return

                self.comboBox_table.clear()
                self.comboBox_table.addItems(tables)
                self.current_table = tables[0]

        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取表列表失败：{str(e)}")

    def switch_table(self, table_name):
        """切换表"""
        self.current_table = table_name
        self.lineEdit_filter.clear()
        self.load_table_data(table_name)

    def load_table_data(self, table_name):
        """加载表数据（增加数据打印，方便排查）"""
        self.source_model.clear()

        try:
            with sqlite3.connect(self.database) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(f"SELECT * FROM {table_name}")
                results = cursor.fetchall()

                # 打印前10条数据，确认数据格式（方便排查筛选问题）
                logger.debug(f"\n表「{table_name}」前10条数据：")
                for i, row in enumerate(results[:10]):
                    logger.debug(f"第{i + 1}条：{dict(row)}")

                # 处理表头
                if results:
                    headers = results[0].keys()
                else:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    headers = [col[1] for col in cursor.fetchall()]
                    QMessageBox.information(self, "提示", f"表「{table_name}」中暂无数据！")
                    return

                self.source_model.setHorizontalHeaderLabels(headers)

                # 填充数据（确保数据是字符串格式）
                for row_idx, row_data in enumerate(results):
                    for col_idx, col_name in enumerate(headers):
                        # 强制转为字符串，避免数据类型不匹配
                        cell_value = str(row_data[col_name]).strip()  # 去除前后空格
                        item = QStandardItem(cell_value)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setEditable(False)
                        self.source_model.setItem(row_idx, col_idx, item)

                # 更新状态标签
                total_count = len(results)
                self.label_status.setText(f"总：{total_count} 条 | 表：{table_name}")
                logger.debug(f"加载表「{table_name}」完成，共 {total_count} 条数据")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载表「{table_name}」失败：{str(e)}")

    def refresh_current_table(self):
        """刷新数据"""
        if self.current_table:
            self.lineEdit_filter.clear()
            self.load_table_data(self.current_table)

    def filter_data(self, filter_text):
        """修复筛选逻辑：优先使用“包含匹配”，兼容所有数据"""
        filter_text = filter_text.strip()  # 去除关键词前后空格

        # 关键修复：如果关键词为空，显示所有数据
        if not filter_text:
            self.proxy_model.setFilterFixedString("")  # 清空筛选
            filtered_count = self.source_model.rowCount()
        else:
            # 方案1：使用“包含匹配”（最稳定，输入关键词直接匹配）
            self.proxy_model.setFilterFixedString(filter_text)

            # （如果方案1不行，注释上面，启用方案2）
            # 方案2：简化模糊匹配（仅在关键词后加%，匹配以关键词开头的内容）
            # self.proxy_model.setFilterWildcard(f"{filter_text}%")

        # 更新状态标签
        total_count = self.source_model.rowCount()
        filtered_count = self.proxy_model.rowCount()
        self.label_status.setText(f"总：{total_count} 条 | 筛选后：{filtered_count} 条 | 表：{self.current_table}")

        # 打印筛选后的前5条数据，确认是否有匹配结果（修复表头获取方式）
        if filtered_count > 0:
            logger.debug(f"筛选后前5条数据：")
            # 正确获取表头：通过 source_model 的 horizontalHeaderItem 获取列名
            headers = []
            for col_idx in range(self.source_model.columnCount()):
                header_item = self.source_model.horizontalHeaderItem(col_idx)
                headers.append(header_item.text() if header_item else f"列{col_idx + 1}")

            for i in range(min(5, filtered_count)):
                row_idx = self.proxy_model.mapToSource(self.proxy_model.index(i, 0)).row()
                row_data = {}
                for col_idx, col_name in enumerate(headers):
                    item = self.source_model.item(row_idx, col_idx)
                    row_data[col_name] = item.text() if item else ""
                logger.debug(f"  第{i + 1}条：{row_data}")
        else:
            logger.debug("无匹配数据（检查关键词是否在数据中）")


# 测试代码
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    sql_panel = SQLTablePanel("../test.db")  # 替换为你的数据库路径
    sql_panel.show()
    sys.exit(app.exec())
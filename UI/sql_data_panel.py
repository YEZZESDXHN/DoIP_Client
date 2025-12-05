import logging
import sqlite3
from typing import Optional

from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtWidgets import QDialog, QHeaderView

from UI.sql_table_ui import Ui_sql

logger = logging.getLogger("UiCustom")


class SQLTablePanel(Ui_sql, QDialog):
    def __init__(self, database_path: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f'SQL可视化面板')

        self.database_path = database_path
        self.database = None
        self.model = None
        self.table_names: Optional[list[str]] = None
        self.init_database()
        self.init_ui()
        self._init_signal_slot()

    def _init_signal_slot(self):
        self.comboBox_table.currentTextChanged.connect(self.change_table)

    def change_table(self, table_name):
        self.model.setTable(table_name)
        self.model.select()

    def init_database(self):
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName(self.database_path)
        if not self.database.open():
            logger.error("数据库打开失败")
            return
        self.model = QSqlTableModel(db=self.database)
        logger.debug(f"数据库打开成功：{self.database_path}")
        self.table_names = self.database.tables()
        logger.debug(f'{self.table_names}')

    def init_ui(self):
        self.model.setTable(self.table_names[0])
        self.model.select()

        self.tableView.setModel(self.model)

        for table_name in self.table_names:
            self.comboBox_table.addItem(table_name)
        self.comboBox_table.setCurrentText(self.table_names[0])








# 测试代码
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    sql_panel = SQLTablePanel("../test.db")  # 替换为你的数据库路径
    sql_panel.show()
    sys.exit(app.exec())
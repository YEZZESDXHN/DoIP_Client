# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sql_table_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect)
from PySide6.QtWidgets import (QComboBox, QTableView)

class Ui_sql(object):
    def setupUi(self, sql):
        if not sql.objectName():
            sql.setObjectName(u"sql")
        sql.resize(880, 374)
        self.tableView = QTableView(sql)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(20, 50, 771, 192))
        self.comboBox_table = QComboBox(sql)
        self.comboBox_table.setObjectName(u"comboBox_table")
        self.comboBox_table.setGeometry(QRect(20, 10, 181, 22))

        self.retranslateUi(sql)

        QMetaObject.connectSlotsByName(sql)
    # setupUi

    def retranslateUi(self, sql):
        sql.setWindowTitle(QCoreApplication.translate("sql", u"Dialog", None))
    # retranslateUi


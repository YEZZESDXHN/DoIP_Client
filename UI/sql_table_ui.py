# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sql_table_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTableView, QWidget)

class Ui_sql(object):
    def setupUi(self, sql):
        if not sql.objectName():
            sql.setObjectName(u"sql")
        sql.resize(880, 374)
        self.tableView = QTableView(sql)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(30, 130, 771, 192))
        self.comboBox_table = QComboBox(sql)
        self.comboBox_table.setObjectName(u"comboBox_table")
        self.comboBox_table.setGeometry(QRect(240, 10, 181, 22))
        self.btn_refresh = QPushButton(sql)
        self.btn_refresh.setObjectName(u"btn_refresh")
        self.btn_refresh.setGeometry(QRect(460, 10, 75, 24))
        self.lineEdit_filter = QLineEdit(sql)
        self.lineEdit_filter.setObjectName(u"lineEdit_filter")
        self.lineEdit_filter.setGeometry(QRect(90, 10, 113, 20))
        self.label_status = QLabel(sql)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setGeometry(QRect(110, 330, 221, 16))
        self.label_filter = QLabel(sql)
        self.label_filter.setObjectName(u"label_filter")
        self.label_filter.setGeometry(QRect(20, 10, 54, 16))

        self.retranslateUi(sql)

        QMetaObject.connectSlotsByName(sql)
    # setupUi

    def retranslateUi(self, sql):
        sql.setWindowTitle(QCoreApplication.translate("sql", u"Dialog", None))
        self.btn_refresh.setText(QCoreApplication.translate("sql", u"\u5237\u65b0", None))
        self.label_status.setText(QCoreApplication.translate("sql", u"TextLabel", None))
        self.label_filter.setText(QCoreApplication.translate("sql", u"\u7b5b\u9009\uff1a", None))
    # retranslateUi


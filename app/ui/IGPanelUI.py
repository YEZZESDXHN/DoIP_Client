# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'IGPanelUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHeaderView, QScrollArea,
    QSizePolicy, QSplitter, QTableView, QVBoxLayout,
    QWidget)

class Ui_IG(object):
    def setupUi(self, IG):
        if not IG.objectName():
            IG.setObjectName(u"IG")
        IG.resize(694, 362)
        self.verticalLayout = QVBoxLayout(IG)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(IG)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableView_messages = QTableView(self.groupBox_2)
        self.tableView_messages.setObjectName(u"tableView_messages")

        self.verticalLayout_2.addWidget(self.tableView_messages)

        self.splitter.addWidget(self.groupBox_2)
        self.scrollArea = QScrollArea(self.splitter)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 690, 167))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.tableView_data = QTableView(self.scrollAreaWidgetContents_4)
        self.tableView_data.setObjectName(u"tableView_data")
        self.tableView_data.setStyleSheet(u"#tableView_data {\n"
"borde: None;\n"
"}")

        self.verticalLayout_3.addWidget(self.tableView_data)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_4)
        self.splitter.addWidget(self.scrollArea)

        self.verticalLayout.addWidget(self.splitter)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(IG)

        QMetaObject.connectSlotsByName(IG)
    # setupUi

    def retranslateUi(self, IG):
        IG.setWindowTitle(QCoreApplication.translate("IG", u"Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("IG", u"IG\u6a21\u5757", None))
    # retranslateUi


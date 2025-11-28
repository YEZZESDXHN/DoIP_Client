# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DoIPConfigUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(602, 300)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.groupBox_DoIPConfig = QGroupBox(Dialog)
        self.groupBox_DoIPConfig.setObjectName(u"groupBox_DoIPConfig")
        self.groupBox_DoIPConfig.setGeometry(QRect(10, 10, 541, 200))
        self.groupBox_DoIPConfig.setMinimumSize(QSize(500, 120))
        self.groupBox_DoIPConfig.setMaximumSize(QSize(600, 200))
        self.layoutWidget = QWidget(self.groupBox_DoIPConfig)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 60, 271, 31))
        self.horizontalLayout_6 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(110, 0))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_6.setFont(font)

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lineEdit_DUTLogicalAddress = QLineEdit(self.layoutWidget)
        self.lineEdit_DUTLogicalAddress.setObjectName(u"lineEdit_DUTLogicalAddress")
        self.lineEdit_DUTLogicalAddress.setFont(font)

        self.horizontalLayout_6.addWidget(self.lineEdit_DUTLogicalAddress)

        self.layoutWidget1 = QWidget(self.groupBox_DoIPConfig)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 10, 341, 41))
        self.horizontalLayout_3 = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QSize(110, 0))
        self.label_3.setSizeIncrement(QSize(0, 0))
        self.label_3.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEdit_TesterLogicalAddress = QLineEdit(self.layoutWidget1)
        self.lineEdit_TesterLogicalAddress.setObjectName(u"lineEdit_TesterLogicalAddress")
        self.lineEdit_TesterLogicalAddress.setMinimumSize(QSize(120, 0))
        self.lineEdit_TesterLogicalAddress.setFont(font)

        self.horizontalLayout_3.addWidget(self.lineEdit_TesterLogicalAddress)

        self.layoutWidget2 = QWidget(self.groupBox_DoIPConfig)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(10, 100, 201, 27))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(60, 0))
        self.label_2.setBaseSize(QSize(0, 0))
        self.label_2.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_DUT_IP = QLineEdit(self.layoutWidget2)
        self.lineEdit_DUT_IP.setObjectName(u"lineEdit_DUT_IP")
        self.lineEdit_DUT_IP.setFont(font)

        self.horizontalLayout_2.addWidget(self.lineEdit_DUT_IP)


        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.groupBox_DoIPConfig.setTitle("")
        self.label_6.setText(QCoreApplication.translate("Dialog", u"DUT \u903b\u8f91\u5730\u5740(Hex)", None))
        self.lineEdit_DUTLogicalAddress.setPlaceholderText(QCoreApplication.translate("Dialog", u"77A", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Tester \u903b\u8f91\u5730\u5740(Hex)", None))
        self.lineEdit_TesterLogicalAddress.setPlaceholderText(QCoreApplication.translate("Dialog", u"7E2", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"DUT IP", None))
        self.lineEdit_DUT_IP.setPlaceholderText(QCoreApplication.translate("Dialog", u"192.168.1.1", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AddDiagServiceDialog.ui'
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
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

class Ui_AddDiagServiceDialog(object):
    def setupUi(self, AddDiagServiceDialog):
        if not AddDiagServiceDialog.objectName():
            AddDiagServiceDialog.setObjectName(u"AddDiagServiceDialog")
        AddDiagServiceDialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(AddDiagServiceDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 281, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.layoutWidget = QWidget(AddDiagServiceDialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(50, 40, 281, 27))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_name = QLineEdit(self.layoutWidget)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setFont(font)

        self.horizontalLayout.addWidget(self.lineEdit_name)

        self.horizontalLayout.setStretch(1, 3)
        self.layoutWidget_2 = QWidget(AddDiagServiceDialog)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(50, 100, 281, 27))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_Hex = QLineEdit(self.layoutWidget_2)
        self.lineEdit_Hex.setObjectName(u"lineEdit_Hex")
        self.lineEdit_Hex.setFont(font)

        self.horizontalLayout_2.addWidget(self.lineEdit_Hex)

        self.horizontalLayout_2.setStretch(1, 3)
        self.label_3 = QLabel(AddDiagServiceDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(50, 150, 281, 20))
        font1 = QFont()
        font1.setBold(False)
        font1.setHintingPreference(QFont.PreferDefaultHinting)
        self.label_3.setFont(font1)
        self.label_3.setStyleSheet(u"color: rgb(139, 139, 139);")
        self.label_3.setFrameShape(QFrame.Shape.NoFrame)
        self.label_3.setFrameShadow(QFrame.Shadow.Sunken)
        self.label_3.setLineWidth(1)
        self.label_3.setTextFormat(Qt.TextFormat.AutoText)

        self.retranslateUi(AddDiagServiceDialog)
        self.buttonBox.rejected.connect(AddDiagServiceDialog.reject)

        QMetaObject.connectSlotsByName(AddDiagServiceDialog)
    # setupUi

    def retranslateUi(self, AddDiagServiceDialog):
        AddDiagServiceDialog.setWindowTitle(QCoreApplication.translate("AddDiagServiceDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8282\u70b9\u540d\u79f0\uff1a", None))
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8bf7\u8f93\u5165\u8282\u70b9\u540d\u79f0\uff08\u5fc5\u586b\uff09", None))
        self.label_2.setText(QCoreApplication.translate("AddDiagServiceDialog", u"Hex\u6570\u636e\uff1a", None))
        self.lineEdit_Hex.setPlaceholderText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8bf7\u8f93\u5165\u5341\u516d\u8fdb\u5236\u5b57\u7b26\u4e32\uff08\u9009\u586b\uff0c\u4f8b\uff1a1A3F\u3001FF00\u300112\uff09", None))
        self.label_3.setText(QCoreApplication.translate("AddDiagServiceDialog", u"\u683c\u5f0f\uff1a\u4ec5\u5141\u8bb80-9\u3001a-f\u3001A-F\uff0c\u7a7a\u5219\u4e3a\u65e0\u6570\u636e", None))
    # retranslateUi


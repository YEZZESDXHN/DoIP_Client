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
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AddDiagServiceDialog(object):
    def setupUi(self, AddDiagServiceDialog):
        if not AddDiagServiceDialog.objectName():
            AddDiagServiceDialog.setObjectName(u"AddDiagServiceDialog")
        AddDiagServiceDialog.resize(440, 246)
        self.verticalLayout_3 = QVBoxLayout(AddDiagServiceDialog)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(AddDiagServiceDialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_name = QLineEdit(AddDiagServiceDialog)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setFont(font)

        self.horizontalLayout.addWidget(self.lineEdit_name)

        self.horizontalLayout.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_Hex = QLabel(AddDiagServiceDialog)
        self.label_Hex.setObjectName(u"label_Hex")
        self.label_Hex.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_Hex)

        self.lineEdit_Hex = QLineEdit(AddDiagServiceDialog)
        self.lineEdit_Hex.setObjectName(u"lineEdit_Hex")
        self.lineEdit_Hex.setFont(font)

        self.horizontalLayout_2.addWidget(self.lineEdit_Hex)

        self.horizontalLayout_2.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.label_note = QLabel(AddDiagServiceDialog)
        self.label_note.setObjectName(u"label_note")
        font1 = QFont()
        font1.setBold(False)
        font1.setHintingPreference(QFont.PreferDefaultHinting)
        self.label_note.setFont(font1)
        self.label_note.setStyleSheet(u"color: rgb(139, 139, 139);")
        self.label_note.setFrameShape(QFrame.Shape.NoFrame)
        self.label_note.setFrameShadow(QFrame.Shadow.Sunken)
        self.label_note.setLineWidth(1)
        self.label_note.setTextFormat(Qt.TextFormat.AutoText)

        self.verticalLayout.addWidget(self.label_note)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.buttonBox = QDialogButtonBox(AddDiagServiceDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_4.addWidget(self.buttonBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.verticalLayout_3.setStretch(0, 5)
        self.verticalLayout_3.setStretch(1, 2)

        self.retranslateUi(AddDiagServiceDialog)
        self.buttonBox.rejected.connect(AddDiagServiceDialog.reject)

        QMetaObject.connectSlotsByName(AddDiagServiceDialog)
    # setupUi

    def retranslateUi(self, AddDiagServiceDialog):
        AddDiagServiceDialog.setWindowTitle(QCoreApplication.translate("AddDiagServiceDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8282\u70b9\u540d\u79f0\uff1a", None))
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8bf7\u8f93\u5165\u8282\u70b9\u540d\u79f0\uff08\u5fc5\u586b\uff09", None))
        self.label_Hex.setText(QCoreApplication.translate("AddDiagServiceDialog", u"Hex\u6570\u636e\uff1a", None))
        self.lineEdit_Hex.setPlaceholderText(QCoreApplication.translate("AddDiagServiceDialog", u"\u8bf7\u8f93\u5165\u5341\u516d\u8fdb\u5236\u5b57\u7b26\u4e32\uff08\u9009\u586b\uff0c\u4f8b\uff1a1A3F\u3001FF00\u300112\uff09", None))
        self.label_note.setText(QCoreApplication.translate("AddDiagServiceDialog", u"\u683c\u5f0f\uff1a\u4ec5\u5141\u8bb80-9\u3001a-f\u3001A-F\uff0c\u7a7a\u5219\u4e3a\u65e0\u6570\u636e", None))
    # retranslateUi


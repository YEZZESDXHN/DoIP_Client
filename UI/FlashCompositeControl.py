# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FlashCompositeControl.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QToolButton, QWidget)

class Ui_Form_FlashChooseFileControl(object):
    def setupUi(self, Form_FlashChooseFileControl):
        if not Form_FlashChooseFileControl.objectName():
            Form_FlashChooseFileControl.setObjectName(u"Form_FlashChooseFileControl")
        Form_FlashChooseFileControl.resize(420, 24)
        self.horizontalLayout = QHBoxLayout(Form_FlashChooseFileControl)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_FlashFileName = QLabel(Form_FlashChooseFileControl)
        self.label_FlashFileName.setObjectName(u"label_FlashFileName")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_FlashFileName.sizePolicy().hasHeightForWidth())
        self.label_FlashFileName.setSizePolicy(sizePolicy)
        self.label_FlashFileName.setMinimumSize(QSize(60, 0))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_FlashFileName.setFont(font)

        self.horizontalLayout.addWidget(self.label_FlashFileName)

        self.lineEdit_FlashFilePath = QLineEdit(Form_FlashChooseFileControl)
        self.lineEdit_FlashFilePath.setObjectName(u"lineEdit_FlashFilePath")

        self.horizontalLayout.addWidget(self.lineEdit_FlashFilePath)

        self.toolButton_LoadFlashFile = QToolButton(Form_FlashChooseFileControl)
        self.toolButton_LoadFlashFile.setObjectName(u"toolButton_LoadFlashFile")

        self.horizontalLayout.addWidget(self.toolButton_LoadFlashFile)


        self.retranslateUi(Form_FlashChooseFileControl)

        QMetaObject.connectSlotsByName(Form_FlashChooseFileControl)
    # setupUi

    def retranslateUi(self, Form_FlashChooseFileControl):
        Form_FlashChooseFileControl.setWindowTitle(QCoreApplication.translate("Form_FlashChooseFileControl", u"Form", None))
        self.label_FlashFileName.setText(QCoreApplication.translate("Form_FlashChooseFileControl", u"Flash file", None))
        self.toolButton_LoadFlashFile.setText(QCoreApplication.translate("Form_FlashChooseFileControl", u"...", None))
    # retranslateUi


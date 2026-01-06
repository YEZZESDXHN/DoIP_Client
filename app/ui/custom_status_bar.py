# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'custom_status_bar.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_CustomStatusBar(object):
    def setupUi(self, CustomStatusBar):
        if not CustomStatusBar.objectName():
            CustomStatusBar.setObjectName(u"CustomStatusBar")
        CustomStatusBar.resize(530, 20)
        self.horizontalLayout = QHBoxLayout(CustomStatusBar)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.pushButton_ConnectState = QPushButton(CustomStatusBar)
        self.pushButton_ConnectState.setObjectName(u"pushButton_ConnectState")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ConnectState.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectState.setSizePolicy(sizePolicy)
        self.pushButton_ConnectState.setMinimumSize(QSize(80, 0))
        self.pushButton_ConnectState.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pushButton_ConnectState.setStyleSheet(u"border: none;                /* \u53bb\u6389\u8fb9\u6846 */\n"
"background: transparent;     /* \u900f\u660e\u80cc\u666f */")

        self.horizontalLayout.addWidget(self.pushButton_ConnectState)

        self.line = QFrame(CustomStatusBar)
        self.line.setObjectName(u"line")
        self.line.setWindowModality(Qt.WindowModality.NonModal)
        font = QFont()
        font.setBold(False)
        font.setHintingPreference(QFont.PreferDefaultHinting)
        self.line.setFont(font)
        self.line.setStyleSheet(u"border: none; background-color: #e0e0e0; width: 1px; margin: 3px 6px;")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.label_SendPrompt = QLabel(CustomStatusBar)
        self.label_SendPrompt.setObjectName(u"label_SendPrompt")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_SendPrompt.sizePolicy().hasHeightForWidth())
        self.label_SendPrompt.setSizePolicy(sizePolicy1)
        self.label_SendPrompt.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.label_SendPrompt)

        self.line_2 = QFrame(CustomStatusBar)
        self.line_2.setObjectName(u"line_2")
        font1 = QFont()
        font1.setBold(False)
        self.line_2.setFont(font1)
        self.line_2.setStyleSheet(u"border: none; background-color: #e0e0e0; width: 1px; margin: 3px 6px;")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_2)

        self.horizontalSpacer = QSpacerItem(291, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_Version = QLabel(CustomStatusBar)
        self.label_Version.setObjectName(u"label_Version")
        sizePolicy.setHeightForWidth(self.label_Version.sizePolicy().hasHeightForWidth())
        self.label_Version.setSizePolicy(sizePolicy)
        self.label_Version.setMinimumSize(QSize(50, 0))

        self.horizontalLayout.addWidget(self.label_Version)


        self.retranslateUi(CustomStatusBar)

        QMetaObject.connectSlotsByName(CustomStatusBar)
    # setupUi

    def retranslateUi(self, CustomStatusBar):
        CustomStatusBar.setWindowTitle(QCoreApplication.translate("CustomStatusBar", u"Form", None))
        self.pushButton_ConnectState.setText(QCoreApplication.translate("CustomStatusBar", u"\u672a\u8fde\u63a5", None))
        self.label_SendPrompt.setText("")
        self.label_Version.setText("")
    # retranslateUi


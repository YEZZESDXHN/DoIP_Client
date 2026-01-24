# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExternalScriptPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ExternalScript_Panel(object):
    def setupUi(self, ExternalScript_Panel):
        if not ExternalScript_Panel.objectName():
            ExternalScript_Panel.setObjectName(u"ExternalScript_Panel")
        ExternalScript_Panel.resize(344, 300)
        self.verticalLayout = QVBoxLayout(ExternalScript_Panel)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(ExternalScript_Panel)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 342, 250))
        self.horizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_start = QPushButton(ExternalScript_Panel)
        self.pushButton_start.setObjectName(u"pushButton_start")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_start.sizePolicy().hasHeightForWidth())
        self.pushButton_start.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.pushButton_start)

        self.pushButton_stop = QPushButton(ExternalScript_Panel)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        sizePolicy.setHeightForWidth(self.pushButton_stop.sizePolicy().hasHeightForWidth())
        self.pushButton_stop.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.pushButton_stop)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.label_State = QLabel(ExternalScript_Panel)
        self.label_State.setObjectName(u"label_State")
        sizePolicy.setHeightForWidth(self.label_State.sizePolicy().hasHeightForWidth())
        self.label_State.setSizePolicy(sizePolicy)
        self.label_State.setMinimumSize(QSize(230, 0))
        self.label_State.setMaximumSize(QSize(16777215, 16777215))
        self.label_State.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_3.addWidget(self.label_State)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(ExternalScript_Panel)

        QMetaObject.connectSlotsByName(ExternalScript_Panel)
    # setupUi

    def retranslateUi(self, ExternalScript_Panel):
        ExternalScript_Panel.setWindowTitle(QCoreApplication.translate("ExternalScript_Panel", u"Form", None))
        self.pushButton_start.setText(QCoreApplication.translate("ExternalScript_Panel", u"\u5f00\u59cb\u8fd0\u884c", None))
        self.pushButton_stop.setText(QCoreApplication.translate("ExternalScript_Panel", u"\u505c\u6b62\u8fd0\u884c", None))
        self.label_State.setText("")
    # retranslateUi


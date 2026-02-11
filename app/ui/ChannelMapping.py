# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ChannelMapping.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QSizePolicy, QSpacerItem, QSplitter,
    QTableView, QVBoxLayout, QWidget)

class Ui_Dialog_ChannelMapping(object):
    def setupUi(self, Dialog_ChannelMapping):
        if not Dialog_ChannelMapping.objectName():
            Dialog_ChannelMapping.setObjectName(u"Dialog_ChannelMapping")
        Dialog_ChannelMapping.resize(688, 494)
        self.verticalLayout_3 = QVBoxLayout(Dialog_ChannelMapping)
        self.verticalLayout_3.setSpacing(9)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.splitter = QSplitter(Dialog_ChannelMapping)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(10)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setStyleSheet(u"#groupBox_2{border: none;}")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label_2)

        self.comboBox = QComboBox(self.groupBox_2)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.comboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.tableView_EthChannels = QTableView(self.groupBox_2)
        self.tableView_EthChannels.setObjectName(u"tableView_EthChannels")

        self.verticalLayout_2.addWidget(self.tableView_EthChannels)

        self.splitter.addWidget(self.groupBox_2)
        self.groupBox = QGroupBox(self.splitter)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"#groupBox{border: none;}")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.label)

        self.comboBox_CanNum = QComboBox(self.groupBox)
        self.comboBox_CanNum.setObjectName(u"comboBox_CanNum")
        self.comboBox_CanNum.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.comboBox_CanNum)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.tableView_CanChannels = QTableView(self.groupBox)
        self.tableView_CanChannels.setObjectName(u"tableView_CanChannels")

        self.verticalLayout.addWidget(self.tableView_CanChannels)

        self.splitter.addWidget(self.groupBox)

        self.verticalLayout_3.addWidget(self.splitter)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.buttonBox = QDialogButtonBox(Dialog_ChannelMapping)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_3.addWidget(self.buttonBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Dialog_ChannelMapping)
        self.buttonBox.accepted.connect(Dialog_ChannelMapping.accept)
        self.buttonBox.rejected.connect(Dialog_ChannelMapping.reject)

        QMetaObject.connectSlotsByName(Dialog_ChannelMapping)
    # setupUi

    def retranslateUi(self, Dialog_ChannelMapping):
        Dialog_ChannelMapping.setWindowTitle(QCoreApplication.translate("Dialog_ChannelMapping", u"Dialog", None))
        self.groupBox_2.setTitle("")
        self.label_2.setText(QCoreApplication.translate("Dialog_ChannelMapping", u"Eth\u901a\u9053\u6570\u91cf", None))
        self.comboBox.setCurrentText("")
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Dialog_ChannelMapping", u"CAN\u901a\u9053\u6570\u91cf", None))
    # retranslateUi


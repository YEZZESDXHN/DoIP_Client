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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSplitter, QTableView,
    QVBoxLayout, QWidget)

class Ui_IG(object):
    def setupUi(self, IG):
        if not IG.objectName():
            IG.setObjectName(u"IG")
        IG.resize(694, 362)
        self.verticalLayout = QVBoxLayout(IG)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.pushButton_NMCANbusConfig = QPushButton(IG)
        self.pushButton_NMCANbusConfig.setObjectName(u"pushButton_NMCANbusConfig")

        self.gridLayout_3.addWidget(self.pushButton_NMCANbusConfig, 1, 3, 1, 1)

        self.label_8 = QLabel(IG)
        self.label_8.setObjectName(u"label_8")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMinimumSize(QSize(60, 0))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_8.setFont(font)

        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)

        self.comboBox_NMHardwareChannel = QComboBox(IG)
        self.comboBox_NMHardwareChannel.setObjectName(u"comboBox_NMHardwareChannel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_NMHardwareChannel.sizePolicy().hasHeightForWidth())
        self.comboBox_NMHardwareChannel.setSizePolicy(sizePolicy1)
        self.comboBox_NMHardwareChannel.setMinimumSize(QSize(150, 0))
        self.comboBox_NMHardwareChannel.setFont(font)
        self.comboBox_NMHardwareChannel.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_3.addWidget(self.comboBox_NMHardwareChannel, 1, 1, 1, 1)

        self.pushButton_NMRefreshCANChannel = QPushButton(IG)
        self.pushButton_NMRefreshCANChannel.setObjectName(u"pushButton_NMRefreshCANChannel")
        sizePolicy.setHeightForWidth(self.pushButton_NMRefreshCANChannel.sizePolicy().hasHeightForWidth())
        self.pushButton_NMRefreshCANChannel.setSizePolicy(sizePolicy)
        self.pushButton_NMRefreshCANChannel.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_NMRefreshCANChannel.setFont(font)

        self.gridLayout_3.addWidget(self.pushButton_NMRefreshCANChannel, 1, 2, 1, 1)

        self.label_10 = QLabel(IG)
        self.label_10.setObjectName(u"label_10")
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMinimumSize(QSize(60, 0))
        self.label_10.setFont(font)

        self.gridLayout_3.addWidget(self.label_10, 0, 0, 1, 1)

        self.comboBox_NMHardwareType = QComboBox(IG)
        self.comboBox_NMHardwareType.setObjectName(u"comboBox_NMHardwareType")
        sizePolicy1.setHeightForWidth(self.comboBox_NMHardwareType.sizePolicy().hasHeightForWidth())
        self.comboBox_NMHardwareType.setSizePolicy(sizePolicy1)
        self.comboBox_NMHardwareType.setMinimumSize(QSize(150, 0))
        self.comboBox_NMHardwareType.setFont(font)
        self.comboBox_NMHardwareType.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_3.addWidget(self.comboBox_NMHardwareType, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 4, 1, 1)

        self.pushButton_NMConnectCANBus = QPushButton(IG)
        self.pushButton_NMConnectCANBus.setObjectName(u"pushButton_NMConnectCANBus")
        sizePolicy.setHeightForWidth(self.pushButton_NMConnectCANBus.sizePolicy().hasHeightForWidth())
        self.pushButton_NMConnectCANBus.setSizePolicy(sizePolicy)
        self.pushButton_NMConnectCANBus.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_NMConnectCANBus.setFont(font)

        self.gridLayout_3.addWidget(self.pushButton_NMConnectCANBus, 0, 5, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)

        self.verticalLayout.addLayout(self.gridLayout_3)

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
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 678, 58))
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

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(IG)

        QMetaObject.connectSlotsByName(IG)
    # setupUi

    def retranslateUi(self, IG):
        IG.setWindowTitle(QCoreApplication.translate("IG", u"Form", None))
        self.pushButton_NMCANbusConfig.setText(QCoreApplication.translate("IG", u"CAN\u63a5\u53e3\u914d\u7f6e", None))
        self.label_8.setText(QCoreApplication.translate("IG", u"\u901a\u9053", None))
        self.pushButton_NMRefreshCANChannel.setText(QCoreApplication.translate("IG", u"\u5237\u65b0", None))
        self.label_10.setText(QCoreApplication.translate("IG", u"\u8bbe\u5907\u63a5\u53e3", None))
        self.pushButton_NMConnectCANBus.setText(QCoreApplication.translate("IG", u"\u8fde\u63a5", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("IG", u"IG\u6a21\u5757", None))
    # retranslateUi


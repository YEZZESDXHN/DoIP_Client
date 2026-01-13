# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'IgBusConfigPanel_ui.ui'
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
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_IgBusConfig(object):
    def setupUi(self, IgBusConfig):
        if not IgBusConfig.objectName():
            IgBusConfig.setObjectName(u"IgBusConfig")
        IgBusConfig.resize(518, 330)
        self.verticalLayout_2 = QVBoxLayout(IgBusConfig)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_CANBusConfig = QGroupBox(IgBusConfig)
        self.groupBox_CANBusConfig.setObjectName(u"groupBox_CANBusConfig")
        self.groupBox_CANBusConfig.setMinimumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_CANBusConfig)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.groupBox_CANBusConfig)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setMinimumSize(QSize(0, 200))
        self.scrollArea_2.setStyleSheet(u"#scrollArea_2 {\n"
"    border: none;\n"
"}")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 498, 263))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_9 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_9.setObjectName(u"label_9")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QSize(95, 0))
        self.label_9.setMaximumSize(QSize(95, 16777215))
        self.label_9.setSizeIncrement(QSize(0, 0))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_9.setFont(font)

        self.horizontalLayout_13.addWidget(self.label_9)

        self.comboBox_CANControllerMode = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_CANControllerMode.addItem("")
        self.comboBox_CANControllerMode.addItem("")
        self.comboBox_CANControllerMode.setObjectName(u"comboBox_CANControllerMode")

        self.horizontalLayout_13.addWidget(self.comboBox_CANControllerMode)


        self.verticalLayout_6.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_16 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setMinimumSize(QSize(95, 0))
        self.label_16.setMaximumSize(QSize(95, 16777215))
        self.label_16.setSizeIncrement(QSize(0, 0))
        self.label_16.setFont(font)

        self.horizontalLayout_20.addWidget(self.label_16)

        self.lineEdit_CANControllerClockFrequency = QLineEdit(self.scrollAreaWidgetContents_2)
        self.lineEdit_CANControllerClockFrequency.setObjectName(u"lineEdit_CANControllerClockFrequency")
        self.lineEdit_CANControllerClockFrequency.setMinimumSize(QSize(120, 0))
        self.lineEdit_CANControllerClockFrequency.setFont(font)

        self.horizontalLayout_20.addWidget(self.lineEdit_CANControllerClockFrequency)


        self.verticalLayout_6.addLayout(self.horizontalLayout_20)

        self.groupBox_arbitration = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_arbitration.setObjectName(u"groupBox_arbitration")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_arbitration)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_11 = QLabel(self.groupBox_arbitration)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setMinimumSize(QSize(95, 0))
        self.label_11.setMaximumSize(QSize(95, 16777215))
        self.label_11.setSizeIncrement(QSize(0, 0))
        self.label_11.setFont(font)

        self.horizontalLayout_15.addWidget(self.label_11)

        self.lineEdit_NormalBitrate = QLineEdit(self.groupBox_arbitration)
        self.lineEdit_NormalBitrate.setObjectName(u"lineEdit_NormalBitrate")
        self.lineEdit_NormalBitrate.setMinimumSize(QSize(120, 0))
        self.lineEdit_NormalBitrate.setFont(font)

        self.horizontalLayout_15.addWidget(self.lineEdit_NormalBitrate)


        self.verticalLayout_7.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_12 = QLabel(self.groupBox_arbitration)
        self.label_12.setObjectName(u"label_12")
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setMinimumSize(QSize(95, 0))
        self.label_12.setMaximumSize(QSize(95, 16777215))
        self.label_12.setSizeIncrement(QSize(0, 0))
        self.label_12.setFont(font)

        self.horizontalLayout_16.addWidget(self.label_12)

        self.lineEdit_NormalSamplePoint = QLineEdit(self.groupBox_arbitration)
        self.lineEdit_NormalSamplePoint.setObjectName(u"lineEdit_NormalSamplePoint")
        self.lineEdit_NormalSamplePoint.setMinimumSize(QSize(120, 0))
        self.lineEdit_NormalSamplePoint.setFont(font)

        self.horizontalLayout_16.addWidget(self.lineEdit_NormalSamplePoint)


        self.verticalLayout_7.addLayout(self.horizontalLayout_16)


        self.verticalLayout_6.addWidget(self.groupBox_arbitration)

        self.groupBox_data = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_data.setObjectName(u"groupBox_data")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_data)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_15 = QLabel(self.groupBox_data)
        self.label_15.setObjectName(u"label_15")
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)
        self.label_15.setMinimumSize(QSize(95, 0))
        self.label_15.setMaximumSize(QSize(95, 16777215))
        self.label_15.setSizeIncrement(QSize(0, 0))
        self.label_15.setFont(font)

        self.horizontalLayout_19.addWidget(self.label_15)

        self.lineEdit_DataBitrate = QLineEdit(self.groupBox_data)
        self.lineEdit_DataBitrate.setObjectName(u"lineEdit_DataBitrate")
        self.lineEdit_DataBitrate.setMinimumSize(QSize(120, 0))
        self.lineEdit_DataBitrate.setFont(font)

        self.horizontalLayout_19.addWidget(self.lineEdit_DataBitrate)


        self.verticalLayout_8.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_14 = QLabel(self.groupBox_data)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setMinimumSize(QSize(95, 0))
        self.label_14.setMaximumSize(QSize(95, 16777215))
        self.label_14.setSizeIncrement(QSize(0, 0))
        self.label_14.setFont(font)

        self.horizontalLayout_18.addWidget(self.label_14)

        self.lineEdit_DataSamplePoint = QLineEdit(self.groupBox_data)
        self.lineEdit_DataSamplePoint.setObjectName(u"lineEdit_DataSamplePoint")
        self.lineEdit_DataSamplePoint.setMinimumSize(QSize(120, 0))
        self.lineEdit_DataSamplePoint.setFont(font)

        self.horizontalLayout_18.addWidget(self.lineEdit_DataSamplePoint)


        self.verticalLayout_8.addLayout(self.horizontalLayout_18)


        self.verticalLayout_6.addWidget(self.groupBox_data)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_4.addWidget(self.scrollArea_2)


        self.verticalLayout_2.addWidget(self.groupBox_CANBusConfig)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonBox = QDialogButtonBox(IgBusConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(IgBusConfig)
        self.buttonBox.rejected.connect(IgBusConfig.reject)

        self.comboBox_CANControllerMode.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(IgBusConfig)
    # setupUi

    def retranslateUi(self, IgBusConfig):
        IgBusConfig.setWindowTitle(QCoreApplication.translate("IgBusConfig", u"Dialog", None))
        self.groupBox_CANBusConfig.setTitle(QCoreApplication.translate("IgBusConfig", u"CAN\u63a7\u5236\u5668", None))
        self.label_9.setText(QCoreApplication.translate("IgBusConfig", u"\u6a21\u5f0f", None))
        self.comboBox_CANControllerMode.setItemText(0, QCoreApplication.translate("IgBusConfig", u"CAN", None))
        self.comboBox_CANControllerMode.setItemText(1, QCoreApplication.translate("IgBusConfig", u"CANFD", None))

        self.label_16.setText(QCoreApplication.translate("IgBusConfig", u"\u65f6\u949f\u9891\u7387", None))
        self.lineEdit_CANControllerClockFrequency.setPlaceholderText(QCoreApplication.translate("IgBusConfig", u"(e.g. 80_000_000)", None))
        self.groupBox_arbitration.setTitle(QCoreApplication.translate("IgBusConfig", u"\u4ef2\u88c1", None))
        self.label_11.setText(QCoreApplication.translate("IgBusConfig", u"\u6ce2\u7279\u7387", None))
        self.lineEdit_NormalBitrate.setPlaceholderText(QCoreApplication.translate("IgBusConfig", u"(e.g. 500_000)", None))
        self.label_12.setText(QCoreApplication.translate("IgBusConfig", u"\u91c7\u6837\u70b9", None))
        self.lineEdit_NormalSamplePoint.setPlaceholderText(QCoreApplication.translate("IgBusConfig", u"(e.g. 80.0)", None))
        self.groupBox_data.setTitle(QCoreApplication.translate("IgBusConfig", u"\u6570\u636e", None))
        self.label_15.setText(QCoreApplication.translate("IgBusConfig", u"\u6ce2\u7279\u7387", None))
        self.lineEdit_DataBitrate.setPlaceholderText(QCoreApplication.translate("IgBusConfig", u"(e.g. 2000_000)", None))
        self.label_14.setText(QCoreApplication.translate("IgBusConfig", u"\u91c7\u6837\u70b9", None))
        self.lineEdit_DataSamplePoint.setPlaceholderText(QCoreApplication.translate("IgBusConfig", u"(e.g. 80.0)", None))
    # retranslateUi


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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QToolButton,
    QVBoxLayout, QWidget)

class Ui_DoIPConfig(object):
    def setupUi(self, DoIPConfig):
        if not DoIPConfig.objectName():
            DoIPConfig.setObjectName(u"DoIPConfig")
        DoIPConfig.resize(725, 793)
        DoIPConfig.setMinimumSize(QSize(500, 0))
        DoIPConfig.setMaximumSize(QSize(1000, 1000))
        self.verticalLayout_9 = QVBoxLayout(DoIPConfig)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_ConfigName = QLabel(DoIPConfig)
        self.label_ConfigName.setObjectName(u"label_ConfigName")
        self.label_ConfigName.setMinimumSize(QSize(95, 0))
        self.label_ConfigName.setMaximumSize(QSize(95, 16777215))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_ConfigName.setFont(font)

        self.horizontalLayout_4.addWidget(self.label_ConfigName)

        self.lineEdit_ConfigName = QLineEdit(DoIPConfig)
        self.lineEdit_ConfigName.setObjectName(u"lineEdit_ConfigName")
        self.lineEdit_ConfigName.setFont(font)

        self.horizontalLayout_4.addWidget(self.lineEdit_ConfigName)

        self.pushButton_delete = QPushButton(DoIPConfig)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_delete.sizePolicy().hasHeightForWidth())
        self.pushButton_delete.setSizePolicy(sizePolicy)
        self.pushButton_delete.setFont(font)

        self.horizontalLayout_4.addWidget(self.pushButton_delete)

        self.horizontalLayout_4.setStretch(1, 3)

        self.verticalLayout_9.addLayout(self.horizontalLayout_4)

        self.groupBox_DoIPConfig = QGroupBox(DoIPConfig)
        self.groupBox_DoIPConfig.setObjectName(u"groupBox_DoIPConfig")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_DoIPConfig.sizePolicy().hasHeightForWidth())
        self.groupBox_DoIPConfig.setSizePolicy(sizePolicy1)
        self.groupBox_DoIPConfig.setMinimumSize(QSize(500, 0))
        self.groupBox_DoIPConfig.setMaximumSize(QSize(9999, 9999))
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_DoIPConfig)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.groupBox_DoIPConfig)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QSize(95, 0))
        self.label_3.setMaximumSize(QSize(95, 16777215))
        self.label_3.setSizeIncrement(QSize(0, 0))
        self.label_3.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEdit_TesterLogicalAddress = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_TesterLogicalAddress.setObjectName(u"lineEdit_TesterLogicalAddress")
        self.lineEdit_TesterLogicalAddress.setMinimumSize(QSize(120, 0))
        self.lineEdit_TesterLogicalAddress.setFont(font)

        self.horizontalLayout_3.addWidget(self.lineEdit_TesterLogicalAddress)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.groupBox_DoIPConfig)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(95, 0))
        self.label_6.setMaximumSize(QSize(95, 16777215))
        self.label_6.setFont(font)

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lineEdit_DUTLogicalAddress = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_DUTLogicalAddress.setObjectName(u"lineEdit_DUTLogicalAddress")
        self.lineEdit_DUTLogicalAddress.setFont(font)

        self.horizontalLayout_6.addWidget(self.lineEdit_DUTLogicalAddress)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.groupBox_DoIPConfig)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(95, 0))
        self.label_2.setMaximumSize(QSize(95, 16777215))
        self.label_2.setBaseSize(QSize(0, 0))
        self.label_2.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_DUT_IP = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_DUT_IP.setObjectName(u"lineEdit_DUT_IP")
        self.lineEdit_DUT_IP.setFont(font)

        self.horizontalLayout_2.addWidget(self.lineEdit_DUT_IP)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.checkBox_RouteActive = QCheckBox(self.groupBox_DoIPConfig)
        self.checkBox_RouteActive.setObjectName(u"checkBox_RouteActive")
        sizePolicy.setHeightForWidth(self.checkBox_RouteActive.sizePolicy().hasHeightForWidth())
        self.checkBox_RouteActive.setSizePolicy(sizePolicy)
        self.checkBox_RouteActive.setMinimumSize(QSize(92, 26))
        self.checkBox_RouteActive.setMaximumSize(QSize(92, 16777215))
        self.checkBox_RouteActive.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_RouteActive.setChecked(True)

        self.horizontalLayout_5.addWidget(self.checkBox_RouteActive)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(3, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label = QLabel(self.groupBox_DoIPConfig)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_OEMSpecific = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_OEMSpecific.setObjectName(u"lineEdit_OEMSpecific")
        self.lineEdit_OEMSpecific.setFont(font)

        self.horizontalLayout.addWidget(self.lineEdit_OEMSpecific)

        self.horizontalLayout.setStretch(2, 3)

        self.horizontalLayout_5.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_9.addLayout(self.verticalLayout)


        self.verticalLayout_9.addWidget(self.groupBox_DoIPConfig)

        self.groupBox_UDSonCANConfig = QGroupBox(DoIPConfig)
        self.groupBox_UDSonCANConfig.setObjectName(u"groupBox_UDSonCANConfig")
        self.groupBox_UDSonCANConfig.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_UDSonCANConfig)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_17 = QLabel(self.groupBox_UDSonCANConfig)
        self.label_17.setObjectName(u"label_17")
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)
        self.label_17.setMinimumSize(QSize(95, 0))
        self.label_17.setMaximumSize(QSize(95, 16777215))
        self.label_17.setSizeIncrement(QSize(0, 0))
        self.label_17.setFont(font)

        self.horizontalLayout_21.addWidget(self.label_17)

        self.checkBox_IsFD = QCheckBox(self.groupBox_UDSonCANConfig)
        self.checkBox_IsFD.setObjectName(u"checkBox_IsFD")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.checkBox_IsFD.sizePolicy().hasHeightForWidth())
        self.checkBox_IsFD.setSizePolicy(sizePolicy2)

        self.horizontalLayout_21.addWidget(self.checkBox_IsFD)


        self.verticalLayout_2.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_5 = QLabel(self.groupBox_UDSonCANConfig)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QSize(95, 0))
        self.label_5.setMaximumSize(QSize(95, 16777215))
        self.label_5.setSizeIncrement(QSize(0, 0))
        self.label_5.setFont(font)

        self.horizontalLayout_10.addWidget(self.label_5)

        self.lineEdit_CANReqID = QLineEdit(self.groupBox_UDSonCANConfig)
        self.lineEdit_CANReqID.setObjectName(u"lineEdit_CANReqID")
        self.lineEdit_CANReqID.setMinimumSize(QSize(120, 0))
        self.lineEdit_CANReqID.setFont(font)

        self.horizontalLayout_10.addWidget(self.lineEdit_CANReqID)


        self.verticalLayout_2.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_7 = QLabel(self.groupBox_UDSonCANConfig)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QSize(95, 0))
        self.label_7.setMaximumSize(QSize(95, 16777215))
        self.label_7.setSizeIncrement(QSize(0, 0))
        self.label_7.setFont(font)

        self.horizontalLayout_11.addWidget(self.label_7)

        self.lineEdit_CANRespID = QLineEdit(self.groupBox_UDSonCANConfig)
        self.lineEdit_CANRespID.setObjectName(u"lineEdit_CANRespID")
        self.lineEdit_CANRespID.setMinimumSize(QSize(120, 0))
        self.lineEdit_CANRespID.setFont(font)

        self.horizontalLayout_11.addWidget(self.lineEdit_CANRespID)


        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_8 = QLabel(self.groupBox_UDSonCANConfig)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMinimumSize(QSize(95, 0))
        self.label_8.setMaximumSize(QSize(95, 16777215))
        self.label_8.setSizeIncrement(QSize(0, 0))
        self.label_8.setFont(font)

        self.horizontalLayout_12.addWidget(self.label_8)

        self.lineEdit_CANFunID = QLineEdit(self.groupBox_UDSonCANConfig)
        self.lineEdit_CANFunID.setObjectName(u"lineEdit_CANFunID")
        self.lineEdit_CANFunID.setMinimumSize(QSize(120, 0))
        self.lineEdit_CANFunID.setFont(font)

        self.horizontalLayout_12.addWidget(self.lineEdit_CANFunID)


        self.verticalLayout_2.addLayout(self.horizontalLayout_12)


        self.verticalLayout_9.addWidget(self.groupBox_UDSonCANConfig)

        self.groupBox_Security = QGroupBox(DoIPConfig)
        self.groupBox_Security.setObjectName(u"groupBox_Security")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_Security)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_4 = QLabel(self.groupBox_Security)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(95, 0))
        self.label_4.setMaximumSize(QSize(95, 16777215))
        self.label_4.setFont(font)

        self.horizontalLayout_8.addWidget(self.label_4)

        self.lineEdit_GenerateKeyExOptPath = QLineEdit(self.groupBox_Security)
        self.lineEdit_GenerateKeyExOptPath.setObjectName(u"lineEdit_GenerateKeyExOptPath")
        self.lineEdit_GenerateKeyExOptPath.setFont(font)

        self.horizontalLayout_8.addWidget(self.lineEdit_GenerateKeyExOptPath)

        self.toolButton_GenerateKeyExOptPath = QToolButton(self.groupBox_Security)
        self.toolButton_GenerateKeyExOptPath.setObjectName(u"toolButton_GenerateKeyExOptPath")

        self.horizontalLayout_8.addWidget(self.toolButton_GenerateKeyExOptPath)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_2 = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.verticalLayout_9.addWidget(self.groupBox_Security)

        self.groupBox_CANTPConfig = QGroupBox(DoIPConfig)
        self.groupBox_CANTPConfig.setObjectName(u"groupBox_CANTPConfig")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_CANTPConfig)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.groupBox_CANTPConfig)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 699, 54))
        self.widget = QWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(30, 20, 253, 27))
        self.horizontalLayout_14 = QHBoxLayout(self.widget)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_10 = QLabel(self.widget)
        self.label_10.setObjectName(u"label_10")
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMinimumSize(QSize(95, 0))
        self.label_10.setMaximumSize(QSize(95, 16777215))
        self.label_10.setSizeIncrement(QSize(0, 0))
        self.label_10.setFont(font)

        self.horizontalLayout_14.addWidget(self.label_10)

        self.lineEdit_CANReqID_3 = QLineEdit(self.widget)
        self.lineEdit_CANReqID_3.setObjectName(u"lineEdit_CANReqID_3")
        self.lineEdit_CANReqID_3.setMinimumSize(QSize(120, 0))
        self.lineEdit_CANReqID_3.setFont(font)

        self.horizontalLayout_14.addWidget(self.lineEdit_CANReqID_3)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_5.addWidget(self.scrollArea)


        self.verticalLayout_9.addWidget(self.groupBox_CANTPConfig)

        self.groupBox_CANBusConfig = QGroupBox(DoIPConfig)
        self.groupBox_CANBusConfig.setObjectName(u"groupBox_CANBusConfig")
        self.groupBox_CANBusConfig.setMinimumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_CANBusConfig)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.groupBox_CANBusConfig)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setMinimumSize(QSize(0, 200))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 687, 299))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_9 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QSize(95, 0))
        self.label_9.setMaximumSize(QSize(95, 16777215))
        self.label_9.setSizeIncrement(QSize(0, 0))
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


        self.verticalLayout_9.addWidget(self.groupBox_CANBusConfig)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.buttonBox = QDialogButtonBox(DoIPConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_7.addWidget(self.buttonBox)


        self.verticalLayout_9.addLayout(self.horizontalLayout_7)

        self.verticalLayout_9.setStretch(5, 1)

        self.retranslateUi(DoIPConfig)
        self.buttonBox.rejected.connect(DoIPConfig.reject)
        self.checkBox_RouteActive.toggled.connect(self.label.setVisible)
        self.checkBox_RouteActive.toggled.connect(self.lineEdit_OEMSpecific.setVisible)

        self.comboBox_CANControllerMode.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(DoIPConfig)
    # setupUi

    def retranslateUi(self, DoIPConfig):
        DoIPConfig.setWindowTitle(QCoreApplication.translate("DoIPConfig", u"Dialog", None))
        self.label_ConfigName.setText(QCoreApplication.translate("DoIPConfig", u"\u914d\u7f6e\u540d\u79f0", None))
        self.pushButton_delete.setText(QCoreApplication.translate("DoIPConfig", u"\u5220\u9664\u914d\u7f6e", None))
        self.groupBox_DoIPConfig.setTitle(QCoreApplication.translate("DoIPConfig", u"UDS on IP\u914d\u7f6e", None))
        self.label_3.setText(QCoreApplication.translate("DoIPConfig", u"\u8bf7\u6c42ID(Hex)", None))
        self.lineEdit_TesterLogicalAddress.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_6.setText(QCoreApplication.translate("DoIPConfig", u"\u5e94\u7b54(Hex)", None))
        self.lineEdit_DUTLogicalAddress.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 77A)", None))
        self.label_2.setText(QCoreApplication.translate("DoIPConfig", u"\u88ab\u6d4b\u4ef6IP", None))
        self.lineEdit_DUT_IP.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 192.168.1.1)", None))
        self.checkBox_RouteActive.setText(QCoreApplication.translate("DoIPConfig", u"RouteActive", None))
        self.label.setText(QCoreApplication.translate("DoIPConfig", u"OEM specific", None))
        self.groupBox_UDSonCANConfig.setTitle(QCoreApplication.translate("DoIPConfig", u"UDS on CAN\u914d\u7f6e", None))
        self.label_17.setText(QCoreApplication.translate("DoIPConfig", u"CANFD", None))
        self.checkBox_IsFD.setText("")
        self.label_5.setText(QCoreApplication.translate("DoIPConfig", u"\u7269\u7406\u5bfb\u5740(Hex)", None))
        self.lineEdit_CANReqID.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_7.setText(QCoreApplication.translate("DoIPConfig", u"\u54cd\u5e94ID(Hex)", None))
        self.lineEdit_CANRespID.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_8.setText(QCoreApplication.translate("DoIPConfig", u"\u529f\u80fd\u5bfb\u5740(Hex)", None))
        self.lineEdit_CANFunID.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.groupBox_Security.setTitle(QCoreApplication.translate("DoIPConfig", u"\u89e3\u9501\u6587\u4ef6", None))
        self.label_4.setText(QCoreApplication.translate("DoIPConfig", u"\u89e3\u9501\u6587\u4ef6", None))
        self.lineEdit_GenerateKeyExOptPath.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"*.dll & *.py", None))
        self.toolButton_GenerateKeyExOptPath.setText(QCoreApplication.translate("DoIPConfig", u"...", None))
        self.groupBox_CANTPConfig.setTitle(QCoreApplication.translate("DoIPConfig", u"CAN TP\u914d\u7f6e", None))
        self.label_10.setText(QCoreApplication.translate("DoIPConfig", u"\u7269\u7406\u5bfb\u5740(Hex)", None))
        self.lineEdit_CANReqID_3.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.groupBox_CANBusConfig.setTitle(QCoreApplication.translate("DoIPConfig", u"CAN\u63a7\u5236\u5668", None))
        self.label_9.setText(QCoreApplication.translate("DoIPConfig", u"\u6a21\u5f0f", None))
        self.comboBox_CANControllerMode.setItemText(0, QCoreApplication.translate("DoIPConfig", u"CAN", None))
        self.comboBox_CANControllerMode.setItemText(1, QCoreApplication.translate("DoIPConfig", u"CANFD", None))

        self.label_16.setText(QCoreApplication.translate("DoIPConfig", u"\u65f6\u949f\u9891\u7387", None))
        self.lineEdit_CANControllerClockFrequency.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.groupBox_arbitration.setTitle(QCoreApplication.translate("DoIPConfig", u"\u4ef2\u88c1", None))
        self.label_11.setText(QCoreApplication.translate("DoIPConfig", u"\u6ce2\u7279\u7387", None))
        self.lineEdit_NormalBitrate.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_12.setText(QCoreApplication.translate("DoIPConfig", u"\u91c7\u6837\u70b9", None))
        self.lineEdit_NormalSamplePoint.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.groupBox_data.setTitle(QCoreApplication.translate("DoIPConfig", u"\u6570\u636e", None))
        self.label_15.setText(QCoreApplication.translate("DoIPConfig", u"\u6ce2\u7279\u7387", None))
        self.lineEdit_DataBitrate.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_14.setText(QCoreApplication.translate("DoIPConfig", u"\u91c7\u6837\u70b9", None))
        self.lineEdit_DataSamplePoint.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
    # retranslateUi


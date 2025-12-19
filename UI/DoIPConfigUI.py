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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget)

class Ui_DoIPConfig(object):
    def setupUi(self, DoIPConfig):
        if not DoIPConfig.objectName():
            DoIPConfig.setObjectName(u"DoIPConfig")
        DoIPConfig.resize(525, 280)
        DoIPConfig.setMinimumSize(QSize(525, 280))
        DoIPConfig.setMaximumSize(QSize(525, 280))
        self.verticalLayout_2 = QVBoxLayout(DoIPConfig)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_DoIPConfig = QGroupBox(DoIPConfig)
        self.groupBox_DoIPConfig.setObjectName(u"groupBox_DoIPConfig")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_DoIPConfig.sizePolicy().hasHeightForWidth())
        self.groupBox_DoIPConfig.setSizePolicy(sizePolicy)
        self.groupBox_DoIPConfig.setMinimumSize(QSize(500, 120))
        self.groupBox_DoIPConfig.setMaximumSize(QSize(9999, 9999))
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_DoIPConfig)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_ConfigName = QLabel(self.groupBox_DoIPConfig)
        self.label_ConfigName.setObjectName(u"label_ConfigName")
        self.label_ConfigName.setMinimumSize(QSize(90, 0))
        self.label_ConfigName.setMaximumSize(QSize(90, 16777215))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label_ConfigName.setFont(font)

        self.horizontalLayout_4.addWidget(self.label_ConfigName)

        self.lineEdit_ConfigName = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_ConfigName.setObjectName(u"lineEdit_ConfigName")
        self.lineEdit_ConfigName.setFont(font)

        self.horizontalLayout_4.addWidget(self.lineEdit_ConfigName)

        self.pushButton_delete = QPushButton(self.groupBox_DoIPConfig)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_delete.sizePolicy().hasHeightForWidth())
        self.pushButton_delete.setSizePolicy(sizePolicy1)
        self.pushButton_delete.setFont(font)

        self.horizontalLayout_4.addWidget(self.pushButton_delete)

        self.horizontalLayout_4.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.groupBox_DoIPConfig)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(90, 0))
        self.label_3.setMaximumSize(QSize(90, 16777215))
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
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMinimumSize(QSize(90, 0))
        self.label_6.setMaximumSize(QSize(90, 16777215))
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
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(90, 0))
        self.label_2.setMaximumSize(QSize(90, 16777215))
        self.label_2.setBaseSize(QSize(0, 0))
        self.label_2.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_DUT_IP = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_DUT_IP.setObjectName(u"lineEdit_DUT_IP")
        self.lineEdit_DUT_IP.setFont(font)

        self.horizontalLayout_2.addWidget(self.lineEdit_DUT_IP)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_4 = QLabel(self.groupBox_DoIPConfig)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(90, 0))
        self.label_4.setFont(font)

        self.horizontalLayout_8.addWidget(self.label_4)

        self.lineEdit_GenerateKeyExOptPath = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_GenerateKeyExOptPath.setObjectName(u"lineEdit_GenerateKeyExOptPath")
        self.lineEdit_GenerateKeyExOptPath.setFont(font)

        self.horizontalLayout_8.addWidget(self.lineEdit_GenerateKeyExOptPath)

        self.toolButton_GenerateKeyExOptPath = QToolButton(self.groupBox_DoIPConfig)
        self.toolButton_GenerateKeyExOptPath.setObjectName(u"toolButton_GenerateKeyExOptPath")

        self.horizontalLayout_8.addWidget(self.toolButton_GenerateKeyExOptPath)


        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.checkBox_RouteActive = QCheckBox(self.groupBox_DoIPConfig)
        self.checkBox_RouteActive.setObjectName(u"checkBox_RouteActive")
        sizePolicy1.setHeightForWidth(self.checkBox_RouteActive.sizePolicy().hasHeightForWidth())
        self.checkBox_RouteActive.setSizePolicy(sizePolicy1)
        self.checkBox_RouteActive.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_RouteActive.setChecked(True)

        self.horizontalLayout_5.addWidget(self.checkBox_RouteActive)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox_DoIPConfig)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_OEMSpecific = QLineEdit(self.groupBox_DoIPConfig)
        self.lineEdit_OEMSpecific.setObjectName(u"lineEdit_OEMSpecific")
        self.lineEdit_OEMSpecific.setFont(font)

        self.horizontalLayout.addWidget(self.lineEdit_OEMSpecific)

        self.horizontalLayout.setStretch(1, 3)

        self.horizontalLayout_5.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_9.addLayout(self.verticalLayout)


        self.verticalLayout_2.addWidget(self.groupBox_DoIPConfig)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.buttonBox = QDialogButtonBox(DoIPConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy1.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy1)
        self.buttonBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_7.addWidget(self.buttonBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.verticalLayout_2.setStretch(0, 1)

        self.retranslateUi(DoIPConfig)
        self.buttonBox.rejected.connect(DoIPConfig.reject)
        self.checkBox_RouteActive.toggled.connect(self.label.setVisible)
        self.checkBox_RouteActive.toggled.connect(self.lineEdit_OEMSpecific.setVisible)

        QMetaObject.connectSlotsByName(DoIPConfig)
    # setupUi

    def retranslateUi(self, DoIPConfig):
        DoIPConfig.setWindowTitle(QCoreApplication.translate("DoIPConfig", u"Dialog", None))
        self.groupBox_DoIPConfig.setTitle("")
        self.label_ConfigName.setText(QCoreApplication.translate("DoIPConfig", u"\u914d\u7f6e\u540d\u79f0", None))
        self.pushButton_delete.setText(QCoreApplication.translate("DoIPConfig", u"\u5220\u9664\u914d\u7f6e", None))
        self.label_3.setText(QCoreApplication.translate("DoIPConfig", u"\u8bf7\u6c42ID(Hex)", None))
        self.lineEdit_TesterLogicalAddress.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 7E2)", None))
        self.label_6.setText(QCoreApplication.translate("DoIPConfig", u"\u5e94\u7b54(Hex)", None))
        self.lineEdit_DUTLogicalAddress.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 77A)", None))
        self.label_2.setText(QCoreApplication.translate("DoIPConfig", u"\u88ab\u6d4b\u4ef6IP", None))
        self.lineEdit_DUT_IP.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"(e.g. 192.168.1.1)", None))
        self.label_4.setText(QCoreApplication.translate("DoIPConfig", u"\u89e3\u9501\u6587\u4ef6", None))
        self.lineEdit_GenerateKeyExOptPath.setPlaceholderText(QCoreApplication.translate("DoIPConfig", u"*.dll & *.py", None))
        self.toolButton_GenerateKeyExOptPath.setText(QCoreApplication.translate("DoIPConfig", u"...", None))
        self.checkBox_RouteActive.setText(QCoreApplication.translate("DoIPConfig", u"RouteActive", None))
        self.label.setText(QCoreApplication.translate("DoIPConfig", u"OEM specific", None))
    # retranslateUi


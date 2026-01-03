# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FlashConfig.ui'
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
    QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSplitter, QVBoxLayout, QWidget)

class Ui_FlashConfig(object):
    def setupUi(self, FlashConfig):
        if not FlashConfig.objectName():
            FlashConfig.setObjectName(u"FlashConfig")
        FlashConfig.resize(646, 702)
        self.verticalLayout_3 = QVBoxLayout(FlashConfig)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(FlashConfig)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_6.addWidget(self.label_3)

        self.lineEdit_dataFormatIdentifier = QLineEdit(self.groupBox)
        self.lineEdit_dataFormatIdentifier.setObjectName(u"lineEdit_dataFormatIdentifier")

        self.horizontalLayout_6.addWidget(self.lineEdit_dataFormatIdentifier)


        self.gridLayout.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(190, 0))

        self.horizontalLayout_5.addWidget(self.label_2)

        self.comboBox_MemorySizeParameterLength = QComboBox(self.groupBox)
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.addItem("")
        self.comboBox_MemorySizeParameterLength.setObjectName(u"comboBox_MemorySizeParameterLength")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_MemorySizeParameterLength.sizePolicy().hasHeightForWidth())
        self.comboBox_MemorySizeParameterLength.setSizePolicy(sizePolicy1)

        self.horizontalLayout_5.addWidget(self.comboBox_MemorySizeParameterLength)


        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QSize(190, 0))

        self.horizontalLayout_7.addWidget(self.label_4)

        self.comboBox_MaxNumberOfBlockLength = QComboBox(self.groupBox)
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.addItem("")
        self.comboBox_MaxNumberOfBlockLength.setObjectName(u"comboBox_MaxNumberOfBlockLength")
        sizePolicy1.setHeightForWidth(self.comboBox_MaxNumberOfBlockLength.sizePolicy().hasHeightForWidth())
        self.comboBox_MaxNumberOfBlockLength.setSizePolicy(sizePolicy1)
        self.comboBox_MaxNumberOfBlockLength.setEditable(True)

        self.horizontalLayout_7.addWidget(self.comboBox_MaxNumberOfBlockLength)


        self.gridLayout.addLayout(self.horizontalLayout_7, 0, 1, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_4.addWidget(self.label)

        self.comboBox_MemoryAddressParameterLength = QComboBox(self.groupBox)
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.addItem("")
        self.comboBox_MemoryAddressParameterLength.setObjectName(u"comboBox_MemoryAddressParameterLength")
        sizePolicy1.setHeightForWidth(self.comboBox_MemoryAddressParameterLength.sizePolicy().hasHeightForWidth())
        self.comboBox_MemoryAddressParameterLength.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.comboBox_MemoryAddressParameterLength)


        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_9.addWidget(self.label_5)

        self.comboBox_Checksum = QComboBox(self.groupBox)
        self.comboBox_Checksum.setObjectName(u"comboBox_Checksum")
        sizePolicy1.setHeightForWidth(self.comboBox_Checksum.sizePolicy().hasHeightForWidth())
        self.comboBox_Checksum.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.comboBox_Checksum)


        self.gridLayout.addLayout(self.horizontalLayout_9, 2, 0, 1, 1)


        self.horizontalLayout_8.addLayout(self.gridLayout)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.splitter = QSplitter(FlashConfig)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.groupBox_files = QGroupBox(self.splitter)
        self.groupBox_files.setObjectName(u"groupBox_files")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_files.sizePolicy().hasHeightForWidth())
        self.groupBox_files.setSizePolicy(sizePolicy2)
        self.verticalLayout = QVBoxLayout(self.groupBox_files)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_AddFile = QPushButton(self.groupBox_files)
        self.pushButton_AddFile.setObjectName(u"pushButton_AddFile")

        self.horizontalLayout.addWidget(self.pushButton_AddFile)

        self.pushButton_RemoveFile = QPushButton(self.groupBox_files)
        self.pushButton_RemoveFile.setObjectName(u"pushButton_RemoveFile")

        self.horizontalLayout.addWidget(self.pushButton_RemoveFile)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.groupBox_files)
        self.groupBox_steps = QGroupBox(self.splitter)
        self.groupBox_steps.setObjectName(u"groupBox_steps")
        sizePolicy2.setHeightForWidth(self.groupBox_steps.sizePolicy().hasHeightForWidth())
        self.groupBox_steps.setSizePolicy(sizePolicy2)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_steps)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_3 = QPushButton(self.groupBox_steps)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.groupBox_steps)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_2.addWidget(self.pushButton_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.splitter.addWidget(self.groupBox_steps)

        self.verticalLayout_3.addWidget(self.splitter)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.buttonBox = QDialogButtonBox(FlashConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_3.addWidget(self.buttonBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.retranslateUi(FlashConfig)
        self.buttonBox.accepted.connect(FlashConfig.accept)
        self.buttonBox.rejected.connect(FlashConfig.reject)

        self.comboBox_MemorySizeParameterLength.setCurrentIndex(4)
        self.comboBox_MaxNumberOfBlockLength.setCurrentIndex(0)
        self.comboBox_MemoryAddressParameterLength.setCurrentIndex(4)
        self.comboBox_Checksum.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(FlashConfig)
    # setupUi

    def retranslateUi(self, FlashConfig):
        FlashConfig.setWindowTitle(QCoreApplication.translate("FlashConfig", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("FlashConfig", u"\u901a\u7528\u4f20\u8f93\u914d\u7f6e", None))
        self.label_3.setText(QCoreApplication.translate("FlashConfig", u"dataFormatIdentifier", None))
        self.lineEdit_dataFormatIdentifier.setText(QCoreApplication.translate("FlashConfig", u"0", None))
        self.label_2.setText(QCoreApplication.translate("FlashConfig", u"\u5185\u5b58\u5927\u5c0f\u5b57\u8282\u6570", None))
        self.comboBox_MemorySizeParameterLength.setItemText(0, QCoreApplication.translate("FlashConfig", u"0", None))
        self.comboBox_MemorySizeParameterLength.setItemText(1, QCoreApplication.translate("FlashConfig", u"1", None))
        self.comboBox_MemorySizeParameterLength.setItemText(2, QCoreApplication.translate("FlashConfig", u"2", None))
        self.comboBox_MemorySizeParameterLength.setItemText(3, QCoreApplication.translate("FlashConfig", u"3", None))
        self.comboBox_MemorySizeParameterLength.setItemText(4, QCoreApplication.translate("FlashConfig", u"4", None))
        self.comboBox_MemorySizeParameterLength.setItemText(5, QCoreApplication.translate("FlashConfig", u"5", None))
        self.comboBox_MemorySizeParameterLength.setItemText(6, QCoreApplication.translate("FlashConfig", u"6", None))
        self.comboBox_MemorySizeParameterLength.setItemText(7, QCoreApplication.translate("FlashConfig", u"7", None))
        self.comboBox_MemorySizeParameterLength.setItemText(8, QCoreApplication.translate("FlashConfig", u"8", None))
        self.comboBox_MemorySizeParameterLength.setItemText(9, QCoreApplication.translate("FlashConfig", u"9", None))
        self.comboBox_MemorySizeParameterLength.setItemText(10, QCoreApplication.translate("FlashConfig", u"10", None))
        self.comboBox_MemorySizeParameterLength.setItemText(11, QCoreApplication.translate("FlashConfig", u"11", None))
        self.comboBox_MemorySizeParameterLength.setItemText(12, QCoreApplication.translate("FlashConfig", u"12", None))
        self.comboBox_MemorySizeParameterLength.setItemText(13, QCoreApplication.translate("FlashConfig", u"13", None))
        self.comboBox_MemorySizeParameterLength.setItemText(14, QCoreApplication.translate("FlashConfig", u"14", None))
        self.comboBox_MemorySizeParameterLength.setItemText(15, QCoreApplication.translate("FlashConfig", u"15", None))

        self.label_4.setText(QCoreApplication.translate("FlashConfig", u"MaxNumberOfBlockLength", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(0, QCoreApplication.translate("FlashConfig", u"None", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(1, QCoreApplication.translate("FlashConfig", u"0x102", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(2, QCoreApplication.translate("FlashConfig", u"0x203", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(3, QCoreApplication.translate("FlashConfig", u"0x402", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(4, QCoreApplication.translate("FlashConfig", u"0x802", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(5, QCoreApplication.translate("FlashConfig", u"0x1602", None))
        self.comboBox_MaxNumberOfBlockLength.setItemText(6, QCoreApplication.translate("FlashConfig", u"0x3202", None))

        self.label.setText(QCoreApplication.translate("FlashConfig", u"\u5185\u5b58\u5730\u5740\u5b57\u8282\u6570", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(0, QCoreApplication.translate("FlashConfig", u"0", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(1, QCoreApplication.translate("FlashConfig", u"1", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(2, QCoreApplication.translate("FlashConfig", u"2", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(3, QCoreApplication.translate("FlashConfig", u"3", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(4, QCoreApplication.translate("FlashConfig", u"4", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(5, QCoreApplication.translate("FlashConfig", u"5", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(6, QCoreApplication.translate("FlashConfig", u"6", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(7, QCoreApplication.translate("FlashConfig", u"7", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(8, QCoreApplication.translate("FlashConfig", u"8", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(9, QCoreApplication.translate("FlashConfig", u"9", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(10, QCoreApplication.translate("FlashConfig", u"10", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(11, QCoreApplication.translate("FlashConfig", u"11", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(12, QCoreApplication.translate("FlashConfig", u"12", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(13, QCoreApplication.translate("FlashConfig", u"13", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(14, QCoreApplication.translate("FlashConfig", u"14", None))
        self.comboBox_MemoryAddressParameterLength.setItemText(15, QCoreApplication.translate("FlashConfig", u"15", None))

        self.label_5.setText(QCoreApplication.translate("FlashConfig", u"Checksum", None))
        self.groupBox_files.setTitle(QCoreApplication.translate("FlashConfig", u"Files Config", None))
        self.pushButton_AddFile.setText(QCoreApplication.translate("FlashConfig", u"Add File", None))
        self.pushButton_RemoveFile.setText(QCoreApplication.translate("FlashConfig", u"Remove File", None))
        self.groupBox_steps.setTitle(QCoreApplication.translate("FlashConfig", u"Steps Config", None))
        self.pushButton_3.setText(QCoreApplication.translate("FlashConfig", u"PushButton", None))
        self.pushButton_4.setText(QCoreApplication.translate("FlashConfig", u"PushButton", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DoIPToolMainUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPlainTextEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSplitter, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1141, 817)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.comboBox_ChooseConfig = QComboBox(self.centralwidget)
        self.comboBox_ChooseConfig.setObjectName(u"comboBox_ChooseConfig")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_ChooseConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ChooseConfig.setSizePolicy(sizePolicy)
        self.comboBox_ChooseConfig.setMinimumSize(QSize(150, 0))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.comboBox_ChooseConfig.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox_ChooseConfig, 1, 1, 1, 1)

        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMinimumSize(QSize(60, 0))
        self.label_6.setFont(font)

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.pushButton_RefreshIP = QPushButton(self.centralwidget)
        self.pushButton_RefreshIP.setObjectName(u"pushButton_RefreshIP")
        sizePolicy1.setHeightForWidth(self.pushButton_RefreshIP.sizePolicy().hasHeightForWidth())
        self.pushButton_RefreshIP.setSizePolicy(sizePolicy1)
        self.pushButton_RefreshIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_RefreshIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_RefreshIP, 0, 2, 1, 1)

        self.pushButton_ConnectDoIP = QPushButton(self.centralwidget)
        self.pushButton_ConnectDoIP.setObjectName(u"pushButton_ConnectDoIP")
        sizePolicy1.setHeightForWidth(self.pushButton_ConnectDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectDoIP.setSizePolicy(sizePolicy1)
        self.pushButton_ConnectDoIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_ConnectDoIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_ConnectDoIP, 0, 5, 1, 1)

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(60, 0))
        self.label_5.setFont(font)

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.comboBox_TesterIP = QComboBox(self.centralwidget)
        self.comboBox_TesterIP.setObjectName(u"comboBox_TesterIP")
        sizePolicy.setHeightForWidth(self.comboBox_TesterIP.sizePolicy().hasHeightForWidth())
        self.comboBox_TesterIP.setSizePolicy(sizePolicy)
        self.comboBox_TesterIP.setMinimumSize(QSize(150, 0))
        self.comboBox_TesterIP.setFont(font)
        self.comboBox_TesterIP.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_2.addWidget(self.comboBox_TesterIP, 0, 1, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 1, 5, 1, 1)

        self.pushButton_EditConfig = QPushButton(self.centralwidget)
        self.pushButton_EditConfig.setObjectName(u"pushButton_EditConfig")
        sizePolicy1.setHeightForWidth(self.pushButton_EditConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_EditConfig.setSizePolicy(sizePolicy1)
        self.pushButton_EditConfig.setMaximumSize(QSize(50, 16777215))
        self.pushButton_EditConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_EditConfig, 1, 2, 1, 1)

        self.checkBox_AotuReconnect = QCheckBox(self.centralwidget)
        self.checkBox_AotuReconnect.setObjectName(u"checkBox_AotuReconnect")
        sizePolicy1.setHeightForWidth(self.checkBox_AotuReconnect.sizePolicy().hasHeightForWidth())
        self.checkBox_AotuReconnect.setSizePolicy(sizePolicy1)
        self.checkBox_AotuReconnect.setChecked(True)
        self.checkBox_AotuReconnect.setAutoRepeat(False)

        self.gridLayout_2.addWidget(self.checkBox_AotuReconnect, 0, 3, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.gridLayout_2.setColumnStretch(3, 1)
        self.gridLayout_2.setColumnStretch(4, 3)
        self.gridLayout_2.setColumnStretch(5, 1)

        self.verticalLayout_5.addLayout(self.gridLayout_2)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_5.addWidget(self.line)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.lineEdit_DoIPRawDate = QLineEdit(self.centralwidget)
        self.lineEdit_DoIPRawDate.setObjectName(u"lineEdit_DoIPRawDate")

        self.horizontalLayout_8.addWidget(self.lineEdit_DoIPRawDate)

        self.pushButton_SendDoIP = QPushButton(self.centralwidget)
        self.pushButton_SendDoIP.setObjectName(u"pushButton_SendDoIP")
        sizePolicy1.setHeightForWidth(self.pushButton_SendDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_SendDoIP.setSizePolicy(sizePolicy1)

        self.horizontalLayout_8.addWidget(self.pushButton_SendDoIP)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(True)
        self.scrollArea_DiagTree = QScrollArea(self.splitter)
        self.scrollArea_DiagTree.setObjectName(u"scrollArea_DiagTree")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea_DiagTree.sizePolicy().hasHeightForWidth())
        self.scrollArea_DiagTree.setSizePolicy(sizePolicy2)
        self.scrollArea_DiagTree.setMinimumSize(QSize(250, 0))
        self.scrollArea_DiagTree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 246, 620))
        self.scrollArea_DiagTree.setWidget(self.scrollAreaWidgetContents)
        self.splitter.addWidget(self.scrollArea_DiagTree)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab_info = QWidget()
        self.tab_info.setObjectName(u"tab_info")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_info)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_ClearText = QPushButton(self.tab_info)
        self.pushButton_ClearText.setObjectName(u"pushButton_ClearText")
        sizePolicy1.setHeightForWidth(self.pushButton_ClearText.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearText.setSizePolicy(sizePolicy1)
        self.pushButton_ClearText.setFont(font)

        self.verticalLayout_3.addWidget(self.pushButton_ClearText)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.plainTextEdit_DataDisplay = QPlainTextEdit(self.tab_info)
        self.plainTextEdit_DataDisplay.setObjectName(u"plainTextEdit_DataDisplay")

        self.verticalLayout_4.addWidget(self.plainTextEdit_DataDisplay)

        self.verticalLayout_4.setStretch(1, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_4)

        self.tabWidget.addTab(self.tab_info, "")
        self.tab_DoIPTrace = QWidget()
        self.tab_DoIPTrace.setObjectName(u"tab_DoIPTrace")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_DoIPTrace)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_ClearDoIPTrace = QPushButton(self.tab_DoIPTrace)
        self.pushButton_ClearDoIPTrace.setObjectName(u"pushButton_ClearDoIPTrace")
        sizePolicy1.setHeightForWidth(self.pushButton_ClearDoIPTrace.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearDoIPTrace.setSizePolicy(sizePolicy1)
        self.pushButton_ClearDoIPTrace.setFont(font)

        self.verticalLayout.addWidget(self.pushButton_ClearDoIPTrace)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.groupBox_DoIPTrace = QGroupBox(self.tab_DoIPTrace)
        self.groupBox_DoIPTrace.setObjectName(u"groupBox_DoIPTrace")

        self.verticalLayout_2.addWidget(self.groupBox_DoIPTrace)

        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab_DoIPTrace, "")
        self.splitter.addWidget(self.tabWidget)

        self.verticalLayout_5.addWidget(self.splitter)

        self.verticalLayout_5.setStretch(3, 1)

        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1141, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.pushButton_RefreshIP.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.pushButton_ConnectDoIP.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Tester IP", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pushButton_EditConfig.setText(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91", None))
        self.checkBox_AotuReconnect.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u91cd\u8fde", None))
        self.pushButton_SendDoIP.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.pushButton_ClearText.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_info), QCoreApplication.translate("MainWindow", u"Info", None))
        self.pushButton_ClearDoIPTrace.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.groupBox_DoIPTrace.setTitle("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_DoIPTrace), QCoreApplication.translate("MainWindow", u"DoIPTrace", None))
    # retranslateUi


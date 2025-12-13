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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSplitter, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1387, 911)
        self.action_database = QAction(MainWindow)
        self.action_database.setObjectName(u"action_database")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_5 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_EditConfig = QPushButton(self.centralwidget)
        self.pushButton_EditConfig.setObjectName(u"pushButton_EditConfig")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_EditConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_EditConfig.setSizePolicy(sizePolicy)
        self.pushButton_EditConfig.setMaximumSize(QSize(50, 16777215))
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.pushButton_EditConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_EditConfig, 1, 2, 1, 1)

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QSize(60, 0))
        self.label_5.setFont(font)

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.pushButton_ConnectDoIP = QPushButton(self.centralwidget)
        self.pushButton_ConnectDoIP.setObjectName(u"pushButton_ConnectDoIP")
        sizePolicy.setHeightForWidth(self.pushButton_ConnectDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectDoIP.setSizePolicy(sizePolicy)
        self.pushButton_ConnectDoIP.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_ConnectDoIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_ConnectDoIP, 0, 5, 1, 1)

        self.comboBox_ChooseConfig = QComboBox(self.centralwidget)
        self.comboBox_ChooseConfig.setObjectName(u"comboBox_ChooseConfig")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_ChooseConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ChooseConfig.setSizePolicy(sizePolicy1)
        self.comboBox_ChooseConfig.setMinimumSize(QSize(150, 0))
        self.comboBox_ChooseConfig.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox_ChooseConfig, 1, 1, 1, 1)

        self.comboBox_TesterIP = QComboBox(self.centralwidget)
        self.comboBox_TesterIP.setObjectName(u"comboBox_TesterIP")
        sizePolicy1.setHeightForWidth(self.comboBox_TesterIP.sizePolicy().hasHeightForWidth())
        self.comboBox_TesterIP.setSizePolicy(sizePolicy1)
        self.comboBox_TesterIP.setMinimumSize(QSize(150, 0))
        self.comboBox_TesterIP.setFont(font)
        self.comboBox_TesterIP.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_2.addWidget(self.comboBox_TesterIP, 0, 1, 1, 1)

        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(60, 0))
        self.label_6.setFont(font)

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.pushButton_RefreshIP = QPushButton(self.centralwidget)
        self.pushButton_RefreshIP.setObjectName(u"pushButton_RefreshIP")
        sizePolicy.setHeightForWidth(self.pushButton_RefreshIP.sizePolicy().hasHeightForWidth())
        self.pushButton_RefreshIP.setSizePolicy(sizePolicy)
        self.pushButton_RefreshIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_RefreshIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_RefreshIP, 0, 2, 1, 1)

        self.checkBox_AotuReconnect = QCheckBox(self.centralwidget)
        self.checkBox_AotuReconnect.setObjectName(u"checkBox_AotuReconnect")
        sizePolicy.setHeightForWidth(self.checkBox_AotuReconnect.sizePolicy().hasHeightForWidth())
        self.checkBox_AotuReconnect.setSizePolicy(sizePolicy)
        self.checkBox_AotuReconnect.setChecked(True)
        self.checkBox_AotuReconnect.setAutoRepeat(False)

        self.gridLayout_2.addWidget(self.checkBox_AotuReconnect, 0, 3, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.pushButton_CreateConfig = QPushButton(self.centralwidget)
        self.pushButton_CreateConfig.setObjectName(u"pushButton_CreateConfig")
        sizePolicy.setHeightForWidth(self.pushButton_CreateConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_CreateConfig.setSizePolicy(sizePolicy)
        self.pushButton_CreateConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_CreateConfig, 1, 3, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)

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
        sizePolicy.setHeightForWidth(self.pushButton_SendDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_SendDoIP.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.pushButton_SendDoIP)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab_info = QWidget()
        self.tab_info.setObjectName(u"tab_info")
        self.plainTextEdit_DataDisplay = QPlainTextEdit(self.tab_info)
        self.plainTextEdit_DataDisplay.setObjectName(u"plainTextEdit_DataDisplay")
        self.plainTextEdit_DataDisplay.setGeometry(QRect(20, 100, 256, 192))
        self.layoutWidget = QWidget(self.tab_info)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 100, 31))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.pushButton_ClearText = QPushButton(self.layoutWidget)
        self.pushButton_ClearText.setObjectName(u"pushButton_ClearText")
        sizePolicy.setHeightForWidth(self.pushButton_ClearText.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearText.setSizePolicy(sizePolicy)
        self.pushButton_ClearText.setFont(font)

        self.verticalLayout_3.addWidget(self.pushButton_ClearText)

        self.tabWidget.addTab(self.tab_info, "")
        self.tab_DoIPTrace = QWidget()
        self.tab_DoIPTrace.setObjectName(u"tab_DoIPTrace")
        self.horizontalLayout = QHBoxLayout(self.tab_DoIPTrace)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 2, 2, 0)
        self.splitter = QSplitter(self.tab_DoIPTrace)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.scrollArea_DiagTree = QScrollArea(self.splitter)
        self.scrollArea_DiagTree.setObjectName(u"scrollArea_DiagTree")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea_DiagTree.sizePolicy().hasHeightForWidth())
        self.scrollArea_DiagTree.setSizePolicy(sizePolicy2)
        self.scrollArea_DiagTree.setMinimumSize(QSize(250, 0))
        self.scrollArea_DiagTree.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea_DiagTree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 248, 737))
        self.scrollArea_DiagTree.setWidget(self.scrollAreaWidgetContents)
        self.splitter.addWidget(self.scrollArea_DiagTree)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_ClearDoIPTrace = QPushButton(self.layoutWidget1)
        self.pushButton_ClearDoIPTrace.setObjectName(u"pushButton_ClearDoIPTrace")
        sizePolicy.setHeightForWidth(self.pushButton_ClearDoIPTrace.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearDoIPTrace.setSizePolicy(sizePolicy)
        self.pushButton_ClearDoIPTrace.setFont(font)

        self.verticalLayout.addWidget(self.pushButton_ClearDoIPTrace)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.groupBox_DoIPTrace = QGroupBox(self.layoutWidget1)
        self.groupBox_DoIPTrace.setObjectName(u"groupBox_DoIPTrace")
        self.groupBox_DoIPTrace.setMinimumSize(QSize(500, 0))

        self.verticalLayout_2.addWidget(self.groupBox_DoIPTrace)

        self.verticalLayout_2.setStretch(1, 1)
        self.splitter.addWidget(self.layoutWidget1)

        self.horizontalLayout.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_DoIPTrace, "")
        self.tab_AutomatedDiagProcess = QWidget()
        self.tab_AutomatedDiagProcess.setObjectName(u"tab_AutomatedDiagProcess")
        self.verticalLayout_6 = QVBoxLayout(self.tab_AutomatedDiagProcess)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(2, 2, 2, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.pushButton = QPushButton(self.tab_AutomatedDiagProcess)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setFont(font)

        self.verticalLayout_7.addWidget(self.pushButton)


        self.verticalLayout_6.addLayout(self.verticalLayout_7)

        self.splitter_3 = QSplitter(self.tab_AutomatedDiagProcess)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Orientation.Horizontal)
        self.tabWidget_2 = QTabWidget(self.splitter_3)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab_DiagStepTree = QWidget()
        self.tab_DiagStepTree.setObjectName(u"tab_DiagStepTree")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_DiagStepTree)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.scrollArea_UdsCaseTree = QScrollArea(self.tab_DiagStepTree)
        self.scrollArea_UdsCaseTree.setObjectName(u"scrollArea_UdsCaseTree")
        self.scrollArea_UdsCaseTree.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 837, 677))
        self.scrollArea_UdsCaseTree.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout_2.addWidget(self.scrollArea_UdsCaseTree)

        self.tabWidget_2.addTab(self.tab_DiagStepTree, "")
        self.tab_DiagServiceTree = QWidget()
        self.tab_DiagServiceTree.setObjectName(u"tab_DiagServiceTree")
        self.verticalLayout_4 = QVBoxLayout(self.tab_DiagServiceTree)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_DiagTreeForProcess = QScrollArea(self.tab_DiagServiceTree)
        self.scrollArea_DiagTreeForProcess.setObjectName(u"scrollArea_DiagTreeForProcess")
        sizePolicy2.setHeightForWidth(self.scrollArea_DiagTreeForProcess.sizePolicy().hasHeightForWidth())
        self.scrollArea_DiagTreeForProcess.setSizePolicy(sizePolicy2)
        self.scrollArea_DiagTreeForProcess.setMinimumSize(QSize(250, 0))
        self.scrollArea_DiagTreeForProcess.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea_DiagTreeForProcess.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTreeForProcess.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTreeForProcess.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 846, 677))
        self.scrollArea_DiagTreeForProcess.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_4.addWidget(self.scrollArea_DiagTreeForProcess)

        self.tabWidget_2.addTab(self.tab_DiagServiceTree, "")
        self.splitter_3.addWidget(self.tabWidget_2)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.groupBox_AutomatedDiagProcessTable = QGroupBox(self.splitter_2)
        self.groupBox_AutomatedDiagProcessTable.setObjectName(u"groupBox_AutomatedDiagProcessTable")
        self.groupBox_AutomatedDiagProcessTable.setMinimumSize(QSize(500, 0))
        self.splitter_2.addWidget(self.groupBox_AutomatedDiagProcessTable)
        self.groupBox_AutomatedDiagTrace = QGroupBox(self.splitter_2)
        self.groupBox_AutomatedDiagTrace.setObjectName(u"groupBox_AutomatedDiagTrace")
        self.splitter_2.addWidget(self.groupBox_AutomatedDiagTrace)
        self.splitter_3.addWidget(self.splitter_2)

        self.verticalLayout_6.addWidget(self.splitter_3)

        self.verticalLayout_6.setStretch(1, 1)
        self.tabWidget.addTab(self.tab_AutomatedDiagProcess, "")

        self.verticalLayout_5.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1387, 22))
        self.menu_about = QMenu(self.menubar)
        self.menu_about.setObjectName(u"menu_about")
        self.menu_set = QMenu(self.menubar)
        self.menu_set.setObjectName(u"menu_set")
        self.menu_tool = QMenu(self.menubar)
        self.menu_tool.setObjectName(u"menu_tool")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menu_tool.menuAction())
        self.menubar.addAction(self.menu_set.menuAction())
        self.menubar.addAction(self.menu_about.menuAction())
        self.menu_tool.addAction(self.action_database)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(2)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_database.setText(QCoreApplication.translate("MainWindow", u"\u53ef\u89c6\u5316\u6570\u636e\u5e93", None))
        self.pushButton_EditConfig.setText(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Tester IP", None))
        self.pushButton_ConnectDoIP.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.pushButton_RefreshIP.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.checkBox_AotuReconnect.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u91cd\u8fde", None))
        self.pushButton_CreateConfig.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u914d\u7f6e", None))
        self.pushButton_SendDoIP.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.pushButton_ClearText.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_info), QCoreApplication.translate("MainWindow", u"Info", None))
        self.pushButton_ClearDoIPTrace.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.groupBox_DoIPTrace.setTitle("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_DoIPTrace), QCoreApplication.translate("MainWindow", u"DoIPTrace", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_DiagStepTree), QCoreApplication.translate("MainWindow", u"UDS\u6d4b\u8bd5\u6d41\u7a0b", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_DiagServiceTree), QCoreApplication.translate("MainWindow", u"\u8bca\u65ad\u670d\u52a1", None))
        self.groupBox_AutomatedDiagProcessTable.setTitle("")
        self.groupBox_AutomatedDiagTrace.setTitle("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_AutomatedDiagProcess), QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u8bca\u65ad\u6d41\u7a0b", None))
        self.menu_about.setTitle(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
        self.menu_set.setTitle(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.menu_tool.setTitle(QCoreApplication.translate("MainWindow", u"\u5de5\u5177", None))
    # retranslateUi


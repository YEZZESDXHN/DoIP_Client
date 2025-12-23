# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UDSToolMainUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDockWidget,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPlainTextEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSplitter, QTabWidget,
    QToolButton, QVBoxLayout, QWidget)

class Ui_UDSToolMainWindow(object):
    def setupUi(self, UDSToolMainWindow):
        if not UDSToolMainWindow.objectName():
            UDSToolMainWindow.setObjectName(u"UDSToolMainWindow")
        UDSToolMainWindow.resize(1387, 911)
        self.action_database = QAction(UDSToolMainWindow)
        self.action_database.setObjectName(u"action_database")
        self.actionReset_View = QAction(UDSToolMainWindow)
        self.actionReset_View.setObjectName(u"actionReset_View")
        self.actionUDS_Services = QAction(UDSToolMainWindow)
        self.actionUDS_Services.setObjectName(u"actionUDS_Services")
        self.actionWrite = QAction(UDSToolMainWindow)
        self.actionWrite.setObjectName(u"actionWrite")
        self.actionUDSCase = QAction(UDSToolMainWindow)
        self.actionUDSCase.setObjectName(u"actionUDSCase")
        self.centralwidget = QWidget(UDSToolMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab_DoIPTrace = QWidget()
        self.tab_DoIPTrace.setObjectName(u"tab_DoIPTrace")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_DoIPTrace)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_ClearDoIPTrace = QPushButton(self.tab_DoIPTrace)
        self.pushButton_ClearDoIPTrace.setObjectName(u"pushButton_ClearDoIPTrace")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ClearDoIPTrace.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearDoIPTrace.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.pushButton_ClearDoIPTrace.setFont(font)

        self.verticalLayout.addWidget(self.pushButton_ClearDoIPTrace)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.groupBox_DoIPTrace = QGroupBox(self.tab_DoIPTrace)
        self.groupBox_DoIPTrace.setObjectName(u"groupBox_DoIPTrace")
        self.groupBox_DoIPTrace.setMinimumSize(QSize(500, 0))

        self.verticalLayout_2.addWidget(self.groupBox_DoIPTrace)

        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab_DoIPTrace, "")
        self.tab_AutomatedDiagProcess = QWidget()
        self.tab_AutomatedDiagProcess.setObjectName(u"tab_AutomatedDiagProcess")
        self.verticalLayout_4 = QVBoxLayout(self.tab_AutomatedDiagProcess)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.pushButton = QPushButton(self.tab_AutomatedDiagProcess)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setFont(font)

        self.verticalLayout_7.addWidget(self.pushButton)


        self.verticalLayout_4.addLayout(self.verticalLayout_7)

        self.splitter_2 = QSplitter(self.tab_AutomatedDiagProcess)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.groupBox_AutomatedDiagProcessTable = QGroupBox(self.splitter_2)
        self.groupBox_AutomatedDiagProcessTable.setObjectName(u"groupBox_AutomatedDiagProcessTable")
        self.groupBox_AutomatedDiagProcessTable.setMinimumSize(QSize(500, 0))
        self.splitter_2.addWidget(self.groupBox_AutomatedDiagProcessTable)
        self.groupBox_AutomatedDiagTrace = QGroupBox(self.splitter_2)
        self.groupBox_AutomatedDiagTrace.setObjectName(u"groupBox_AutomatedDiagTrace")
        self.splitter_2.addWidget(self.groupBox_AutomatedDiagTrace)

        self.verticalLayout_4.addWidget(self.splitter_2)

        self.tabWidget.addTab(self.tab_AutomatedDiagProcess, "")
        self.tab_ExternalScript = QWidget()
        self.tab_ExternalScript.setObjectName(u"tab_ExternalScript")
        self.pushButton_ExternalScriptRun = QPushButton(self.tab_ExternalScript)
        self.pushButton_ExternalScriptRun.setObjectName(u"pushButton_ExternalScriptRun")
        self.pushButton_ExternalScriptRun.setGeometry(QRect(70, 70, 95, 28))
        self.pushButton_ExternalScriptStop = QPushButton(self.tab_ExternalScript)
        self.pushButton_ExternalScriptStop.setObjectName(u"pushButton_ExternalScriptStop")
        self.pushButton_ExternalScriptStop.setGeometry(QRect(70, 120, 95, 28))
        self.toolButton_LoadExternalScript = QToolButton(self.tab_ExternalScript)
        self.toolButton_LoadExternalScript.setObjectName(u"toolButton_LoadExternalScript")
        self.toolButton_LoadExternalScript.setGeometry(QRect(500, 10, 24, 24))
        self.lineEdit_ExternalScriptPath = QLineEdit(self.tab_ExternalScript)
        self.lineEdit_ExternalScriptPath.setObjectName(u"lineEdit_ExternalScriptPath")
        self.lineEdit_ExternalScriptPath.setGeometry(QRect(80, 10, 311, 24))
        self.tabWidget.addTab(self.tab_ExternalScript, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        UDSToolMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(UDSToolMainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1387, 33))
        self.menu_about = QMenu(self.menubar)
        self.menu_about.setObjectName(u"menu_about")
        self.menu_set = QMenu(self.menubar)
        self.menu_set.setObjectName(u"menu_set")
        self.menu_tool = QMenu(self.menubar)
        self.menu_tool.setObjectName(u"menu_tool")
        self.menu_view = QMenu(self.menubar)
        self.menu_view.setObjectName(u"menu_view")
        UDSToolMainWindow.setMenuBar(self.menubar)
        self.dockWidget = QDockWidget(UDSToolMainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidget.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea)
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_EditConfig = QPushButton(self.dockWidgetContents_3)
        self.pushButton_EditConfig.setObjectName(u"pushButton_EditConfig")
        sizePolicy.setHeightForWidth(self.pushButton_EditConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_EditConfig.setSizePolicy(sizePolicy)
        self.pushButton_EditConfig.setMaximumSize(QSize(50, 16777215))
        self.pushButton_EditConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_EditConfig, 1, 2, 1, 1)

        self.label_5 = QLabel(self.dockWidgetContents_3)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QSize(60, 0))
        self.label_5.setFont(font)

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.pushButton_ConnectDoIP = QPushButton(self.dockWidgetContents_3)
        self.pushButton_ConnectDoIP.setObjectName(u"pushButton_ConnectDoIP")
        sizePolicy.setHeightForWidth(self.pushButton_ConnectDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectDoIP.setSizePolicy(sizePolicy)
        self.pushButton_ConnectDoIP.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_ConnectDoIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_ConnectDoIP, 0, 5, 1, 1)

        self.comboBox_ChooseConfig = QComboBox(self.dockWidgetContents_3)
        self.comboBox_ChooseConfig.setObjectName(u"comboBox_ChooseConfig")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_ChooseConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ChooseConfig.setSizePolicy(sizePolicy1)
        self.comboBox_ChooseConfig.setMinimumSize(QSize(150, 0))
        self.comboBox_ChooseConfig.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox_ChooseConfig, 1, 1, 1, 1)

        self.comboBox_TesterIP = QComboBox(self.dockWidgetContents_3)
        self.comboBox_TesterIP.setObjectName(u"comboBox_TesterIP")
        sizePolicy1.setHeightForWidth(self.comboBox_TesterIP.sizePolicy().hasHeightForWidth())
        self.comboBox_TesterIP.setSizePolicy(sizePolicy1)
        self.comboBox_TesterIP.setMinimumSize(QSize(150, 0))
        self.comboBox_TesterIP.setFont(font)
        self.comboBox_TesterIP.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_2.addWidget(self.comboBox_TesterIP, 0, 1, 1, 1)

        self.label_6 = QLabel(self.dockWidgetContents_3)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(60, 0))
        self.label_6.setFont(font)

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.pushButton_RefreshIP = QPushButton(self.dockWidgetContents_3)
        self.pushButton_RefreshIP.setObjectName(u"pushButton_RefreshIP")
        sizePolicy.setHeightForWidth(self.pushButton_RefreshIP.sizePolicy().hasHeightForWidth())
        self.pushButton_RefreshIP.setSizePolicy(sizePolicy)
        self.pushButton_RefreshIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_RefreshIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_RefreshIP, 0, 2, 1, 1)

        self.checkBox_AotuReconnect = QCheckBox(self.dockWidgetContents_3)
        self.checkBox_AotuReconnect.setObjectName(u"checkBox_AotuReconnect")
        sizePolicy.setHeightForWidth(self.checkBox_AotuReconnect.sizePolicy().hasHeightForWidth())
        self.checkBox_AotuReconnect.setSizePolicy(sizePolicy)
        self.checkBox_AotuReconnect.setChecked(True)
        self.checkBox_AotuReconnect.setAutoRepeat(False)

        self.gridLayout_2.addWidget(self.checkBox_AotuReconnect, 0, 3, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.pushButton_CreateConfig = QPushButton(self.dockWidgetContents_3)
        self.pushButton_CreateConfig.setObjectName(u"pushButton_CreateConfig")
        sizePolicy.setHeightForWidth(self.pushButton_CreateConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_CreateConfig.setSizePolicy(sizePolicy)
        self.pushButton_CreateConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_CreateConfig, 1, 3, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)

        self.verticalLayout_5.addLayout(self.gridLayout_2)

        self.line = QFrame(self.dockWidgetContents_3)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_5.addWidget(self.line)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.lineEdit_DoIPRawDate = QLineEdit(self.dockWidgetContents_3)
        self.lineEdit_DoIPRawDate.setObjectName(u"lineEdit_DoIPRawDate")

        self.horizontalLayout_8.addWidget(self.lineEdit_DoIPRawDate)

        self.pushButton_SendDoIP = QPushButton(self.dockWidgetContents_3)
        self.pushButton_SendDoIP.setObjectName(u"pushButton_SendDoIP")
        sizePolicy.setHeightForWidth(self.pushButton_SendDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_SendDoIP.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.pushButton_SendDoIP)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBox_TesterPresent = QCheckBox(self.dockWidgetContents_3)
        self.checkBox_TesterPresent.setObjectName(u"checkBox_TesterPresent")

        self.horizontalLayout_3.addWidget(self.checkBox_TesterPresent)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.dockWidget.setWidget(self.dockWidgetContents_3)
        UDSToolMainWindow.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dockWidget)
        self.dockWidget_DiagTree = QDockWidget(UDSToolMainWindow)
        self.dockWidget_DiagTree.setObjectName(u"dockWidget_DiagTree")
        self.dockWidget_DiagTree.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable|QDockWidget.DockWidgetFeature.DockWidgetFloatable|QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dockWidget_DiagTree.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea|Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout_8 = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_DiagTree = QScrollArea(self.dockWidgetContents_4)
        self.scrollArea_DiagTree.setObjectName(u"scrollArea_DiagTree")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea_DiagTree.sizePolicy().hasHeightForWidth())
        self.scrollArea_DiagTree.setSizePolicy(sizePolicy2)
        self.scrollArea_DiagTree.setMinimumSize(QSize(0, 0))
        self.scrollArea_DiagTree.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea_DiagTree.setSizeIncrement(QSize(0, 0))
        self.scrollArea_DiagTree.setBaseSize(QSize(0, 0))
        self.scrollArea_DiagTree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_DiagTree.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 80, 435))
        self.scrollArea_DiagTree.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_8.addWidget(self.scrollArea_DiagTree)

        self.dockWidget_DiagTree.setWidget(self.dockWidgetContents_4)
        UDSToolMainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget_DiagTree)
        self.dockWidget_UdsCaseTree = QDockWidget(UDSToolMainWindow)
        self.dockWidget_UdsCaseTree.setObjectName(u"dockWidget_UdsCaseTree")
        self.dockWidget_UdsCaseTree.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea|Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.verticalLayout_9 = QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_UdsCaseTree = QScrollArea(self.dockWidgetContents_5)
        self.scrollArea_UdsCaseTree.setObjectName(u"scrollArea_UdsCaseTree")
        self.scrollArea_UdsCaseTree.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 80, 435))
        self.scrollArea_UdsCaseTree.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_9.addWidget(self.scrollArea_UdsCaseTree)

        self.dockWidget_UdsCaseTree.setWidget(self.dockWidgetContents_5)
        UDSToolMainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget_UdsCaseTree)
        self.dockWidget_write = QDockWidget(UDSToolMainWindow)
        self.dockWidget_write.setObjectName(u"dockWidget_write")
        self.dockWidget_write.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea|Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents_6 = QWidget()
        self.dockWidgetContents_6.setObjectName(u"dockWidgetContents_6")
        self.horizontalLayout_4 = QHBoxLayout(self.dockWidgetContents_6)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_DataDisplay = QPlainTextEdit(self.dockWidgetContents_6)
        self.plainTextEdit_DataDisplay.setObjectName(u"plainTextEdit_DataDisplay")
        font1 = QFont()
        font1.setFamilies([u"Microsoft YaHei"])
        self.plainTextEdit_DataDisplay.setFont(font1)

        self.horizontalLayout_4.addWidget(self.plainTextEdit_DataDisplay)

        self.dockWidget_write.setWidget(self.dockWidgetContents_6)
        UDSToolMainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dockWidget_write)

        self.menubar.addAction(self.menu_tool.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menubar.addAction(self.menu_set.menuAction())
        self.menubar.addAction(self.menu_about.menuAction())
        self.menu_tool.addAction(self.action_database)
        self.menu_view.addSeparator()

        self.retranslateUi(UDSToolMainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(UDSToolMainWindow)
    # setupUi

    def retranslateUi(self, UDSToolMainWindow):
        UDSToolMainWindow.setWindowTitle(QCoreApplication.translate("UDSToolMainWindow", u"MainWindow", None))
        self.action_database.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u53ef\u89c6\u5316\u6570\u636e\u5e93", None))
        self.actionReset_View.setText(QCoreApplication.translate("UDSToolMainWindow", u"Reset View", None))
        self.actionUDS_Services.setText(QCoreApplication.translate("UDSToolMainWindow", u"UDS Services", None))
        self.actionWrite.setText(QCoreApplication.translate("UDSToolMainWindow", u"Write", None))
        self.actionUDSCase.setText(QCoreApplication.translate("UDSToolMainWindow", u"UDS\u6d4b\u8bd5\u6d41\u7a0b", None))
        self.pushButton_ClearDoIPTrace.setText(QCoreApplication.translate("UDSToolMainWindow", u"Clear", None))
        self.groupBox_DoIPTrace.setTitle("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_DoIPTrace), QCoreApplication.translate("UDSToolMainWindow", u"\u8bca\u65ad\u63a7\u5236\u53f0", None))
        self.pushButton.setText(QCoreApplication.translate("UDSToolMainWindow", u"Run", None))
        self.groupBox_AutomatedDiagProcessTable.setTitle("")
        self.groupBox_AutomatedDiagTrace.setTitle("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_AutomatedDiagProcess), QCoreApplication.translate("UDSToolMainWindow", u"\u81ea\u52a8\u8bca\u65ad\u6d41\u7a0b", None))
        self.pushButton_ExternalScriptRun.setText(QCoreApplication.translate("UDSToolMainWindow", u"Run", None))
        self.pushButton_ExternalScriptStop.setText(QCoreApplication.translate("UDSToolMainWindow", u"Stop", None))
        self.toolButton_LoadExternalScript.setText(QCoreApplication.translate("UDSToolMainWindow", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExternalScript), QCoreApplication.translate("UDSToolMainWindow", u"\u5916\u90e8\u811a\u672c", None))
        self.menu_about.setTitle(QCoreApplication.translate("UDSToolMainWindow", u"\u5173\u4e8e", None))
        self.menu_set.setTitle(QCoreApplication.translate("UDSToolMainWindow", u"\u8bbe\u7f6e", None))
        self.menu_tool.setTitle(QCoreApplication.translate("UDSToolMainWindow", u"\u5de5\u5177", None))
        self.menu_view.setTitle(QCoreApplication.translate("UDSToolMainWindow", u"\u89c6\u56fe", None))
        self.pushButton_EditConfig.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u7f16\u8f91", None))
        self.label_5.setText(QCoreApplication.translate("UDSToolMainWindow", u"Tester IP", None))
        self.pushButton_ConnectDoIP.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u8fde\u63a5", None))
        self.label_6.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u914d\u7f6e", None))
        self.pushButton_RefreshIP.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u5237\u65b0", None))
        self.checkBox_AotuReconnect.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u81ea\u52a8\u91cd\u8fde", None))
        self.pushButton_CreateConfig.setText(QCoreApplication.translate("UDSToolMainWindow", u"\u65b0\u5efa\u914d\u7f6e", None))
        self.pushButton_SendDoIP.setText(QCoreApplication.translate("UDSToolMainWindow", u"Send", None))
        self.checkBox_TesterPresent.setText(QCoreApplication.translate("UDSToolMainWindow", u"Tester Present", None))
        self.dockWidget_DiagTree.setWindowTitle(QCoreApplication.translate("UDSToolMainWindow", u"UDS Services", None))
        self.dockWidget_UdsCaseTree.setWindowTitle(QCoreApplication.translate("UDSToolMainWindow", u"UDS\u6d4b\u8bd5\u6d41\u7a0b", None))
        self.dockWidget_write.setWindowTitle(QCoreApplication.translate("UDSToolMainWindow", u"Write", None))
    # retranslateUi


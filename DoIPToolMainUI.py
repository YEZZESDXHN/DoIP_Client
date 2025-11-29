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
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPlainTextEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableView, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(896, 817)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(560, 750, 281, 27))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setFont(font)

        self.horizontalLayout.addWidget(self.lineEdit_2)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(310, 750, 75, 23))
        self.pushButton.setFont(font)
        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(20, 120, 491, 30))
        self.horizontalLayout_8 = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_DoIPRawDate = QLineEdit(self.layoutWidget1)
        self.lineEdit_DoIPRawDate.setObjectName(u"lineEdit_DoIPRawDate")

        self.horizontalLayout_8.addWidget(self.lineEdit_DoIPRawDate)

        self.pushButton_SendDoIP = QPushButton(self.layoutWidget1)
        self.pushButton_SendDoIP.setObjectName(u"pushButton_SendDoIP")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_SendDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_SendDoIP.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.pushButton_SendDoIP)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(430, 760, 62, 18))
        self.label_2.setFrameShape(QFrame.Shape.NoFrame)
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(20, 10, 751, 80))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.comboBox_ChooseConfig = QComboBox(self.gridLayoutWidget_2)
        self.comboBox_ChooseConfig.setObjectName(u"comboBox_ChooseConfig")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_ChooseConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ChooseConfig.setSizePolicy(sizePolicy1)
        self.comboBox_ChooseConfig.setMinimumSize(QSize(150, 0))
        self.comboBox_ChooseConfig.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox_ChooseConfig, 1, 1, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(60, 0))
        self.label_6.setFont(font)

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.pushButton_RefreshIP = QPushButton(self.gridLayoutWidget_2)
        self.pushButton_RefreshIP.setObjectName(u"pushButton_RefreshIP")
        sizePolicy.setHeightForWidth(self.pushButton_RefreshIP.sizePolicy().hasHeightForWidth())
        self.pushButton_RefreshIP.setSizePolicy(sizePolicy)
        self.pushButton_RefreshIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_RefreshIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_RefreshIP, 0, 2, 1, 1)

        self.pushButton_ConnectDoIP = QPushButton(self.gridLayoutWidget_2)
        self.pushButton_ConnectDoIP.setObjectName(u"pushButton_ConnectDoIP")
        sizePolicy.setHeightForWidth(self.pushButton_ConnectDoIP.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectDoIP.setSizePolicy(sizePolicy)
        self.pushButton_ConnectDoIP.setMaximumSize(QSize(50, 16777215))
        self.pushButton_ConnectDoIP.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_ConnectDoIP, 0, 5, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QSize(60, 0))
        self.label_5.setFont(font)

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.comboBox_TesterIP = QComboBox(self.gridLayoutWidget_2)
        self.comboBox_TesterIP.setObjectName(u"comboBox_TesterIP")
        sizePolicy1.setHeightForWidth(self.comboBox_TesterIP.sizePolicy().hasHeightForWidth())
        self.comboBox_TesterIP.setSizePolicy(sizePolicy1)
        self.comboBox_TesterIP.setMinimumSize(QSize(150, 0))
        self.comboBox_TesterIP.setFont(font)
        self.comboBox_TesterIP.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_2.addWidget(self.comboBox_TesterIP, 0, 1, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 1, 5, 1, 1)

        self.pushButton_EditConfig = QPushButton(self.gridLayoutWidget_2)
        self.pushButton_EditConfig.setObjectName(u"pushButton_EditConfig")
        sizePolicy.setHeightForWidth(self.pushButton_EditConfig.sizePolicy().hasHeightForWidth())
        self.pushButton_EditConfig.setSizePolicy(sizePolicy)
        self.pushButton_EditConfig.setMaximumSize(QSize(50, 16777215))
        self.pushButton_EditConfig.setFont(font)

        self.gridLayout_2.addWidget(self.pushButton_EditConfig, 1, 2, 1, 1)

        self.checkBox_AotuReconnect = QCheckBox(self.gridLayoutWidget_2)
        self.checkBox_AotuReconnect.setObjectName(u"checkBox_AotuReconnect")
        sizePolicy.setHeightForWidth(self.checkBox_AotuReconnect.sizePolicy().hasHeightForWidth())
        self.checkBox_AotuReconnect.setSizePolicy(sizePolicy)
        self.checkBox_AotuReconnect.setChecked(True)
        self.checkBox_AotuReconnect.setAutoRepeat(False)

        self.gridLayout_2.addWidget(self.checkBox_AotuReconnect, 0, 3, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.gridLayout_2.setColumnStretch(3, 1)
        self.gridLayout_2.setColumnStretch(4, 3)
        self.gridLayout_2.setColumnStretch(5, 1)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(30, 190, 781, 471))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.plainTextEdit_DataDisplay = QPlainTextEdit(self.tab)
        self.plainTextEdit_DataDisplay.setObjectName(u"plainTextEdit_DataDisplay")
        self.plainTextEdit_DataDisplay.setGeometry(QRect(30, 20, 451, 111))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tableView_DoIPTrace = QTableView(self.tab_2)
        self.tableView_DoIPTrace.setObjectName(u"tableView_DoIPTrace")
        self.tableView_DoIPTrace.setGeometry(QRect(20, 30, 741, 391))
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 896, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_SendDoIP.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.pushButton_RefreshIP.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.pushButton_ConnectDoIP.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Tester IP", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pushButton_EditConfig.setText(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91", None))
        self.checkBox_AotuReconnect.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u91cd\u8fde", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
    # retranslateUi


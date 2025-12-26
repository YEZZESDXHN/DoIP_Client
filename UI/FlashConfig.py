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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QHBoxLayout, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_FlashConfig(object):
    def setupUi(self, FlashConfig):
        if not FlashConfig.objectName():
            FlashConfig.setObjectName(u"FlashConfig")
        FlashConfig.resize(519, 479)
        self.buttonBox = QDialogButtonBox(FlashConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(60, 400, 181, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.groupBox_files = QGroupBox(FlashConfig)
        self.groupBox_files.setObjectName(u"groupBox_files")
        self.groupBox_files.setGeometry(QRect(10, 10, 411, 141))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_files.sizePolicy().hasHeightForWidth())
        self.groupBox_files.setSizePolicy(sizePolicy)
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

        self.groupBox_steps = QGroupBox(FlashConfig)
        self.groupBox_steps.setObjectName(u"groupBox_steps")
        self.groupBox_steps.setGeometry(QRect(10, 170, 411, 161))
        sizePolicy.setHeightForWidth(self.groupBox_steps.sizePolicy().hasHeightForWidth())
        self.groupBox_steps.setSizePolicy(sizePolicy)
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


        self.retranslateUi(FlashConfig)
        self.buttonBox.accepted.connect(FlashConfig.accept)
        self.buttonBox.rejected.connect(FlashConfig.reject)

        QMetaObject.connectSlotsByName(FlashConfig)
    # setupUi

    def retranslateUi(self, FlashConfig):
        FlashConfig.setWindowTitle(QCoreApplication.translate("FlashConfig", u"Dialog", None))
        self.groupBox_files.setTitle(QCoreApplication.translate("FlashConfig", u"Files Config", None))
        self.pushButton_AddFile.setText(QCoreApplication.translate("FlashConfig", u"Add File", None))
        self.pushButton_RemoveFile.setText(QCoreApplication.translate("FlashConfig", u"Remove File", None))
        self.groupBox_steps.setTitle(QCoreApplication.translate("FlashConfig", u"Steps Config", None))
        self.pushButton_3.setText(QCoreApplication.translate("FlashConfig", u"PushButton", None))
        self.pushButton_4.setText(QCoreApplication.translate("FlashConfig", u"PushButton", None))
    # retranslateUi


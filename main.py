import logging.config
import sys
from PySide6.QtWidgets import QApplication

from app.windows.MainWindow import MainWindow

# 日志配置
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger('UDSTool')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

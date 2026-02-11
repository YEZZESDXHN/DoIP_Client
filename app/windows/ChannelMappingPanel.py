import sys

from PySide6.QtWidgets import QDialog, QApplication

from app.resources.resources import IconEngine
from app.ui.ChannelMapping import Ui_Dialog_ChannelMapping


class ChannelMappingPanel(Ui_Dialog_ChannelMapping, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("ChannelMapping")
        self.setWindowIcon(IconEngine.get_icon('config'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = ChannelMappingPanel()
    panel.show()
    sys.exit(app.exec())
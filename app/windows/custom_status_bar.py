from PySide6.QtWidgets import QWidget

from app.ui.custom_status_bar import Ui_CustomStatusBar


class CustomStatusBar(Ui_CustomStatusBar, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
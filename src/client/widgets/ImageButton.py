from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

from ..styles import Styles


class ImageButton(QPushButton):
    """Button that displays an image"""

    def __init__(self, image_path, parent=None, size=(32, 32)):
        super().__init__(parent)
        self.setIcon(QIcon("src/resources/" + image_path))
        self.setIconSize(QSize(size[0], size[1]))
        self.setFixedSize(size[0] + 10, size[1] + 10)  # Add padding
        self.setStyleSheet(Styles.IMAGE_BUTTON)

    def change_icon(self, image_path):
        self.setIcon(QIcon("src/resources/" + image_path))

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent

from ..styles import Styles
from .ImageButton import ImageButton


class CustomTitleBar(QWidget):
    """Custom title bar with minimize and close buttons"""

    # Signals
    closeClicked = Signal()
    minimizeClicked = Signal()

    def __init__(self, title="GlobalTags", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(Styles.TITLE_BAR)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Button style
        button_style = Styles.WINDOW_BAR_BUTTON

        # Minimize button
        self.minimize_button = ImageButton("minimize_icon", self, size=(16, 16))
        self.minimize_button.setStyleSheet(button_style)
        self.minimize_button.clicked.connect(self.minimizeClicked.emit)

        # Close button
        self.close_button = ImageButton("close_icon", self, size=(16, 16))
        self.close_button.setStyleSheet(button_style)
        self.close_button.clicked.connect(self.closeClicked.emit)

        # Add widgets to layout
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.close_button)

        # Set fixed height
        self.setFixedHeight(40)

        # Moving logic
        self._dragging = False
        self._dragPos = QPoint()

    def setTitle(self, title):
        """Set the title displayed in the title bar"""
        self.title_label.setText(title)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._dragPos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton and self._dragging:
            self.parent.move(event.globalPosition().toPoint() - self._dragPos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

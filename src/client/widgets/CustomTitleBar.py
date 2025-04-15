from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent

from ..styles import Styles


class CustomTitleBar(QWidget):
    """Custom title bar with minimize and close buttons"""

    # Signals
    closeClicked = Signal()
    minimizeClicked = Signal()

    def __init__(self, title="Window Title", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")

        # Button style
        button_style = Styles.WINDOW_BAR_BUTTON

        # Minimize button
        self.minimize_button = QPushButton("—")
        self.minimize_button.setStyleSheet(button_style)
        self.minimize_button.clicked.connect(self.minimizeClicked.emit)

        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setStyleSheet(button_style + "QPushButton:hover { background-color: #d9534f; color: white; }")
        self.close_button.clicked.connect(self.closeClicked.emit)

        # Add widgets to layout
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.close_button)

        # Set fixed height
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #ddd;")

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

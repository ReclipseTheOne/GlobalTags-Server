from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from ..styles import Styles


class ServerStatItem(QWidget):
    """Widget to display a server statistic with label and value"""

    def __init__(self, label_text, initial_value="N/A"):
        super().__init__()
        self.is_on = True

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)

        # Label
        self.label = QLabel(label_text)
        self.label.setStyleSheet(Styles.STATS_LABEL)
        self.layout.addWidget(self.label)

        # Value
        self.value = initial_value
        self.text = QLabel(self.value)
        self.text.setStyleSheet(Styles.STATS_VALUE)
        self.layout.addWidget(self.text)

    def update_value(self, new_value):
        """Update the displayed value"""
        self.value = new_value
        if self.is_on:
            self.text.setText(str(new_value))
        else:
            self.text.setText(str(new_value))

    def power(self, power: bool):
        self.is_on = power
        self.update_value(self.value)

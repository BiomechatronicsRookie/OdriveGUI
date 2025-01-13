from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel)
from PyQt5.QtCore import Qt
class TopBarWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        # Top bar Layout
        self.motor_dropdown = QComboBox()
        self.refresh_button = QPushButton("Refresh Motors")
        self.reboot_button = QPushButton("Reboot Motor")
        self.state = QLabel()
        self.state.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.motor_dropdown)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.reboot_button)
        layout.addWidget(self.state)
        self.setLayout(layout)
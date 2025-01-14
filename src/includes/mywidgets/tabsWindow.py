from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QButtonGroup,
    QLabel,
    QTabWidget)

from .tabs.motor_info_tab import MotorParameterWidget

class TabsMainWidget(QWidget):
    def __init__(self, motor=None):
        super().__init__()
        self.tabs = QTabWidget()
        self.Tab1 = self.tabs.addTab(MotorParameterWidget(motor), 'Motor Info.')

        layout = QHBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QButtonGroup,
    QLabel,
    QTabWidget)

from .motor_info_tab import MotorParameterWidget

class TabsMainWidget(QWidget):
    def __init__(self, motor=None):
        super().__init__()
        self.tabs = QTabWidget()
        self.Tab1 = self.tabs.addTab(MotorParameterWidget(motor), 'Motor Info.')

        self.control = QWidget()
        self.control_layout = QHBoxLayout()
        # Create three toggle buttons
        self.button1 = QPushButton("Position Control")
        self.button1.setCheckable(True)

        self.button2 = QPushButton("Velocity Control")
        self.button2.setCheckable(True)

        self.button3 = QPushButton("Idle")
        self.button3.setCheckable(True)

        self.button4 = QPushButton("Calibrate")
        self.button4.setCheckable(True)

        # Create a label to show the selected option
        self.label = QLabel("No option selected")

        # Add buttons to a QButtonGroup to make them mutually exclusive
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.button1, 1)  # ID = 1
        self.button_group.addButton(self.button2, 2)  # ID = 2
        self.button_group.addButton(self.button3, 3)  # ID = 3
        self.button_group.addButton(self.button4, 4)  # ID = 3

        # Add widgets to the layout
        self.control_layout.addWidget(self.button1)
        self.control_layout.addWidget(self.button2)
        self.control_layout.addWidget(self.button3)
        self.control_layout.addWidget(self.button4)
        self.control.setLayout(self.control_layout)

        layout = QHBoxLayout()
        layout.addWidget(self.tabs,1)
        layout.addWidget(self.control,1)
        self.setLayout(layout)

        layout = QHBoxLayout()
        self.setLayout(layout)


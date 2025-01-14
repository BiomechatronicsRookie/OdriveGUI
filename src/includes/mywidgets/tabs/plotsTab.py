import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QButtonGroup
import pyqtgraph as pg

class PlotsTab(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        # General layout
        layout = QVBoxLayout()
        # Buttons on top of the plot
        self.control_top_panel = QWidget()
        self.control_top_panel_layout = QHBoxLayout()

        # Create three toggle buttons
        self.button1 = QPushButton("Position Control")
        self.button1.setCheckable(True)

        self.button2 = QPushButton("Velocity Control")
        self.button2.setCheckable(True)

        self.button3 = QPushButton("Torque Control")
        self.button3.setCheckable(True)

        self.button4 = QPushButton("Idle")
        self.button4.setCheckable(True)

        # Add buttons to a QButtonGroup to make them mutually exclusive
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.button1, 1)  # ID = 1
        self.button_group.addButton(self.button2, 2)  # ID = 2
        self.button_group.addButton(self.button3, 3)  # ID = 3
        self.button_group.addButton(self.button4, 4)  # ID = 3

        # Add widgets to the layout
        self.control_top_panel_layout.addWidget(self.button1)
        self.control_top_panel_layout.addWidget(self.button2)
        self.control_top_panel_layout.addWidget(self.button3)
        self.control_top_panel_layout.addWidget(self.button4)
        self.control_top_panel.setLayout(self.control_top_panel_layout)

        self.graph_widget = pg.PlotWidget()

        layout.addWidget(self.control_top_panel,1)
        layout.addWidget(self.graph_widget,7)
        self.setLayout(layout)

        self._configure_plot()

    def _configure_plot(self):
        # Set white background
        self.graph_widget.setBackground('w')

        # Add grid to the plot
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)  # alpha controls the transparency of the grid

        # Remove default auto-scaling
        self.graph_widget.setAutoVisible(y=False)

        # Show axes
        self.graph_widget.showAxis('left', True)
        self.graph_widget.showAxis('bottom', True)

        # Hide the default plot items
        self.graph_widget.clear()

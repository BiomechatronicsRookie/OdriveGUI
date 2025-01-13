from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QTableWidget,
    QTableWidgetItem
    )
from PyQt5.QtCore import Qt, QTimer

class MotorParameterWidget(QWidget):
    def __init__(self, motor = None):
        super().__init__()
        if motor:
            self.motor = motor.axis0
            # Create a QSplitter to hold the tables
            self.splitter = QSplitter(Qt.Vertical)

            # Create the two tables
            self.table1 = QTableWidget()
            self.table2 = QTableWidget()

            # Add the tables to the splitter
            self.splitter.addWidget(self.table1)
            self.splitter.addWidget(self.table2)

            # Ensure the splitter occupies all available space
            self.splitter.setStretchFactor(0, 10)
            self.splitter.setStretchFactor(1, 10)

            # Set up the layout
            layout = QVBoxLayout()
            layout.addWidget(self.splitter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

            # Populate the tables initially
            self.populate_tables()

            # Set up the QTimer for periodic updates
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.populate_tables)
            self.timer.start(200)  # Refresh every `refresh_interval` ms
        else:
            pass

    def populate_tables(self):
        """
        Refresh both tables with the latest motor parameters.
        """
        self.populate_table1()
        self.populate_table2()

    def populate_table1(self):
        """
        Populate the first table with controller parameters.
        """
        # Controller-related parameters
        parameter_map = {
            "Velocity Setpoint": self.motor.controller.input_vel,
            "Position Setpoint": self.motor.controller.input_pos
        }

        # Set up the table
        self.table1.setRowCount(len(parameter_map))
        self.table1.setColumnCount(2)
        self.table1.setHorizontalHeaderLabels(["Controller Parameter", "Value"])

        # Fill the table with parameter data
        for row, (param_name, param_value) in enumerate(parameter_map.items()):
            self.table1.setItem(row, 0, QTableWidgetItem(param_name))
            self.table1.setItem(row, 1, QTableWidgetItem(str(param_value)))

    def populate_table2(self):
        """
        Populate the second table with encoder and motor parameters.
        """
        # Encoder and motor-related parameters
        parameter_map = {
            "Measured Velocity": self.motor.encoder.vel_estimate,
            "Measured Position": self.motor.encoder.pos_estimate,
            "Current Measured": self.motor.motor.current_control.Iq_measured}

        # Set up the table
        self.table2.setRowCount(len(parameter_map))
        self.table2.setColumnCount(2)
        self.table2.setHorizontalHeaderLabels(["Encoder/Motor Parameter", "Value"])

        # Fill the table with parameter data
        for row, (param_name, param_value) in enumerate(parameter_map.items()):
            self.table2.setItem(row, 0, QTableWidgetItem(param_name))
            self.table2.setItem(row, 1, QTableWidgetItem(str(param_value)))
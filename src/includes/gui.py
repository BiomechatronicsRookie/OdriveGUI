import sys
import numpy as np
import time
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QComboBox,
    QTabWidget,
    QTableWidget,
    QSplitter
)
from PyQt5.QtCore import Qt, QTimer
import odrive
from .mywidgets.topbar import TopBarWidget
from .mywidgets.tabs import TabsMainWidget
from odrive.enums import *

class ODriveGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ODrive Motor Controller")

        # Helper object fields
        self.motors = []
        self.curr_motor = 0

        # Main layout
        self.main_layout = QVBoxLayout()
        # Top Bar
        self.top_bar = TopBarWidget()
        # Main Window
        self.tab_window = TabsMainWidget()

        # Combine layouts
        self.main_layout.addWidget(self.top_bar, 1)
        self.main_layout.addWidget(self.tab_window, 3)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # SIGNAL CONNECTION FROM WIDGETS TO GUI FUNCTIONALITY
        # Top Bar
        self.top_bar.refresh_button.clicked.connect(self.refresh_motor_list)
        self.top_bar.reboot_button.clicked.connect(self.reboot_motor)
        self.top_bar.motor_dropdown.activated.connect(self._QComboBox_activated)

        # Control Buttons
        self.tab_window.button_group.buttonClicked[int].connect(self.on_control_button_clicked)

        # Initial refresh
        self.refresh_motor_list()

        # Timers
        # Set up the QTimer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._get_motor_state)
        self.timer.start(200)  # Refresh every `refresh_interval` ms


    # TOP BAR HELPER FUNCTIONS
    def _QComboBox_activated(self, index):
        self.curr_motor = index
        # Select a Widget to replace
        index_to_replace = self.main_layout.indexOf(self.tab_window)

        # Remove the widget from the layout
        if self.tab_window is not None:
            self.tab_window.setParent(None)
        # Recreate the widget
        self.tab_window = TabsMainWidget(self.motors[index])
        #Insert it
        self.main_layout.insertWidget(index_to_replace, self.tab_window,3)


    def refresh_motor_list(self):
        """Refresh the list of connected motors."""
        self.motors = []
        self.motors, self.motor_ids = self.get_connected_motors()
        self.top_bar.motor_dropdown.clear()
        if self.motors:
            self.top_bar.motor_dropdown.addItems(self.motor_ids)

    def get_connected_motors(self):
        """Fetch the list of connected motors."""
        motors = []         # Create a motor list
        motor_ids = []      # Create list to hold all the serial numbers
        try:
            odrives = [odrive.find_any(timeout=1)]  # Detect all connected motors
            if odrives:
                self.curr_motor = 0
                for i, odrv in enumerate(odrives):
                    try:
                        motors.append(odrv)
                        motor_ids.append(str(odrv.serial_number))
                    except Exception as e:
                        error_message = f"Error fetching details for ODrive {odrv.serial_number}: {e}"
                        print(error_message)

        except Exception as e:
            print(f"Error finding ODrives: {e}")
        return motors, motor_ids

    def reboot_motor(self):
        self.motors[self.curr_motor].reboot()
        time.sleep(1)
        self.refresh_motor_list()

    def on_control_button_clicked(self, button_id):
        """
        Handle button click events and update the label.
        """
        if button_id == 1:
            # Activate Position mode
            self.motors[self.curr_motor].axis0.config.control_mode = ControlMode.CONTROL_MODE_POSITION_CONTROL
            self.motors[self.curr_motor].axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
        elif button_id == 2:
            # Activate Velocity mode
            pass
        elif button_id == 3:
            # Activate Idle Mode
            self.motors[self.curr_motor].axis0.requested_state = AxisState.IDLE
        elif button_id == 4:
            # Activate Calibration
            self.motors[self.curr_motor].axis0.requested_state = AxisState.STARTUP_SEQUENCE
            self.motors[self.curr_motor].axis0.requested_state = AxisState.MOTOR_CALIBRATION

    def _get_motor_state(self):
        if self.motors:
            self.top_bar.state.setText("State: " + str(self.motors[self.curr_motor].axis0.current_state))
        else:
            self.top_bar.state.setText('-')
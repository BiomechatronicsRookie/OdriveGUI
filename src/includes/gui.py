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
import pyqtgraph as pg
import odrive
from .mywidgets.topbar import TopBarWidget
from .mywidgets.tabsWindow import TabsMainWidget
from .mywidgets.tabs.plotsTab import PlotsTab
from .mywidgets.dataBuffer import DataBuffer
from odrive.enums import *

class ODriveGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ODrive Motor Controller")
        #self.setFixedWidth(int(1920*0.75))
        #self.setFixedHeight(int(1080*0.75))
        # Helper object fields
        self.motors = []
        self.curr_motor = 0
        self.data_buffer = None
        self.buffer_len = 50
        self.plot_buffer_len = 5000
        self.phase = 0  # A variable to control animation
        self.plot_active = False
        self.mode = None
        self.static_helper = np.linspace(1,5000,5000)
        self.pos_plot_buffer = []
        self.vel_plot_buffer = []
        self.torque_plot_buffer = []

        # Main layout
        self.main_layout = QVBoxLayout()
        # Top Bar
        self.top_bar = TopBarWidget()
        self.bottom_bar =  QWidget()
        self.bottom_bar_layout = QHBoxLayout()
        self.bottom_bar.setLayout(self.bottom_bar_layout)
        # Main Window
        self.tab_window = TabsMainWidget()
        self.plot_window = PlotsTab()

        self.bottom_bar_layout.addWidget(self.tab_window, 2)
        self.bottom_bar_layout.addWidget(self.plot_window, 5)

        # Combine layouts
        self.main_layout.addWidget(self.top_bar, 1)
        self.main_layout.addWidget(self.bottom_bar, 3)

        self.container = QWidget()
        self.container.setLayout(self.main_layout)
        self.setCentralWidget(self.container)

        # SIGNAL CONNECTION FROM WIDGETS TO GUI FUNCTIONALITY
        # Top Bar
        self.top_bar.refresh_button.clicked.connect(self.refresh_motor_list)
        self.top_bar.reboot_button.clicked.connect(self.reboot_motor)
        self.top_bar.motor_dropdown.activated.connect(self._QComboBox_activated)

        # Control Buttons
        self.plot_window.button_group.buttonClicked[int].connect(self.on_control_button_clicked)
        self.plot_window.button1_setpoint.returnPressed.connect(self._set_setpoint)

        # Timers
        # Set up the QTimer for periodic updates
        self.timer_datapoll = QTimer(self)
        self.timer_datapoll.timeout.connect(self._get_motor_state)
        self.timer_datapoll.start(200)  # Refresh every `refresh_interval` ms

    # TOP BAR HELPER FUNCTIONS
    def _QComboBox_activated(self, index):
        self.curr_motor = index
        # Select a Widget to replace
        index_to_replace = self.bottom_bar_layout.indexOf(self.tab_window)

        # Remove the widget from the layout
        geometry, parent = self.tab_window.geometry(), self.tab_window.parent()
        if self.tab_window is not None:
            self.tab_window.setParent(None)
        # Recreate the widget
        self.tab_window = TabsMainWidget(self.motors[index])
        self.tab_window.setParent(parent)
        self.tab_window.setGeometry(geometry)
        #Insert it
        self.bottom_bar_layout.insertWidget(index_to_replace, self.tab_window,2)


    def refresh_motor_list(self):
        """Refresh the list of connected motors."""
        self.motors = []
        self.motors, self.motor_ids = self.get_connected_motors()
        self.top_bar.motor_dropdown.clear()
        if self.motors:
            self.top_bar.motor_dropdown.addItems(self.motor_ids)
            if not self.timer_datapoll.isActive():
                not self.timer_datapoll.start()
            self.data_buffer = DataBuffer(batch_size= self.buffer_len, motor = self.motors[self.curr_motor])
            self.data_buffer.data_batch_ready.connect(self._update_plot)
            self.data_buffer.start()


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
        self.timer_datapoll.stop()
        self.timer_plot.stop()
        self.motors[self.curr_motor].reboot()
        time.sleep(6)
        self.refresh_motor_list()

    def on_control_button_clicked(self, button_id):
        """
        Handle button click events and update the label.
        """
        if button_id == 1:
            # Activate Position mode
            #print(self.motors[self.curr_motor])
            self.motors[self.curr_motor].axis0.controller.config.control_mode = ControlMode.POSITION_CONTROL
            self.motors[self.curr_motor].axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            self.plot_active = True
        elif button_id == 2:
            # Activate Velocity mode
            self.motors[self.curr_motor].axis0.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
            self.motors[self.curr_motor].axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            self.plot_active = True
        elif button_id == 3:
            # Activate Torque Mode
            self.motors[self.curr_motor].axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
            self.motors[self.curr_motor].axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            self.plot_active = True
        elif button_id == 4:
            # Activate Calibration
            self.motors[self.curr_motor].axis0.requested_state = AxisState.IDLE
            self.plot_active = False

        self.mode = self.motors[self.curr_motor].axis0.controller.config.control_mode

    def _set_setpoint(self):
        if self.motors:
            match self.mode:
                case 3:
                    self.motors[self.curr_motor].axis0.controller.input_pos = self.plot_window.button1_setpoint.text()
                case 2:
                    self.motors[self.curr_motor].axis0.controller.input_vel = self.plot_window.button1_setpoint.text()
                case 1:
                    self.motors[self.curr_motor].axis0.controller.input_torque = self.plot_window.button1_setpoint.text()

    def _get_motor_state(self):
        if self.motors:
            self.top_bar.state.setText("State: " + str(self.motors[self.curr_motor].axis0.current_state))
        else:
            self.top_bar.state.setText('-')

    def _update_plot(self, batch):
        """Update the plot with new data."""
        # Generate sine wave data with an animated phase
        if self.plot_active:
            match self.mode:
                case 3:
                    self.pos_plot_buffer.extend(batch[0])
                    self.vel_plot_buffer.extend(batch[1])
                    if len(self.pos_plot_buffer) == self.plot_buffer_len:
                        self.pos_plot_buffer = [self.pos_plot_buffer.pop() for idx in range(self.buffer_len)]
                        self.vel_plot_buffer = [self.vel_plot_buffer.pop() for idx in range(self.buffer_len)]
                    self.plot_window.graph_widget.clear()  # Clear previous data
                    self.plot_window.graph_widget.plot(self.static_helper[0:len(self.pos_plot_buffer)], np.array(self.pos_plot_buffer).ravel(), pen=pg.mkPen(color="b", width=2))
                    self.plot_window.graph_widget.plot(self.static_helper[0:len(self.vel_plot_buffer)], np.array(self.vel_plot_buffer).ravel(), pen=pg.mkPen(color="r", width=2))

                case 2:
                    self.vel_plot_buffer.extend(batch[1])
                    if len(self.vel_plot_buffer) == self.plot_buffer_len:
                        self.vel_plot_buffer = [self.vel_plot_buffer.pop() for idx in range(self.buffer_len)]
                    self.plot_window.graph_widget.clear()  # Clear previous data
                    self.plot_window.graph_widget.plot(self.static_helper[0:len(self.vel_plot_buffer)], np.array(self.vel_plot_buffer).ravel(), pen=pg.mkPen(color="r", width=2))
                case 1:
                    self.torque_plot_buffer.extend(batch[2])
                    if len(self.torque_plot_buffer) == self.plot_buffer_len:
                        self.torque_plot_buffer = [self.torque_plot_buffer.pop() for idx in range(self.buffer_len)]
                    self.plot_window.graph_widget.clear()  # Clear previous data
                    self.plot_window.graph_widget.plot(self.static_helper[0:len(self.torque_plot_buffer)], np.array(self.torque_plot_buffer).ravel(), pen=pg.mkPen(color="r", width=2))

    def closeEvent(self, event):
        for i in self.motors:
            i.axis0.requested_state = AxisState.IDLE
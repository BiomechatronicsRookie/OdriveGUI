from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
import time

class DataBuffer(QThread):

    data_batch_ready = pyqtSignal(list)  # Signal to send a batch of data

    def __init__(self, batch_size=50, motor = None):
        super().__init__()
        self.batch_size = batch_size
        self.running = True
        self.motor = motor

    def run(self):
        pos_batch = [None]*self.batch_size
        vel_batch = [None]*self.batch_size
        torque_batch = [None]*self.batch_size
        n = 0

        while self.running:
            # Simulate high-speed sensor reading
            pos_batch[n] =  self.motor.axis0.encoder.pos_estimate # Replace with actual sensor data
            vel_batch[n] =  self.motor.axis0.encoder.vel_estimate # Replace with actual sensor data
            torque_batch[n] =  self.motor.axis0.motor.I_bus * self.motor.axis0.motor.config.torque_constant # Replace with actual sensor data
            n = n+1

            if n == self.batch_size:
                batch = [pos_batch, vel_batch, torque_batch]
                self.data_batch_ready.emit(batch)  # Send the batch to the UI
                batch = []  # Clear the batch
                n = 0


    def stop(self):
        self.running = False
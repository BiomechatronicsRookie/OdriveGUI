import numpy as no
import odrive
from includes.gui import ODriveGUI
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QPushButton, QComboBox, QTextEdit
)

def main():
    app = QApplication(sys.argv)
    window = ODriveGUI()
    window.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
#!/usr/bin/python3

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from mainWindow import MainWindow


app = QApplication(sys.argv)
m = MainWindow()
m.show()

app.exec_()


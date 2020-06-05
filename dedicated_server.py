#!/usr/bin/python3

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from serverCli import ServerCli

from mainWindow import MainWindow


app = QApplication(sys.argv)
server = ServerCli()


app.exec_()

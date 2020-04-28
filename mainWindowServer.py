from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QByteArray
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
import random, time

from minefieldGui import MinefieldGui
from multiplayerControlsGui import MultiplayerControlsGui
from serverGui import ServerGui
from gameLogic import GameLogic
from serverLogic import GameServer

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Multiplayer Minesweeper")
        self.setGeometry(50, 50, 500, 500)

        gui = ServerGui(self)
        logic = GameServer(self)
        self.m = gui
        self.setCentralWidget(gui)

        gui.start.connect(logic.start)

        logic.gameStarted.connect(gui.reset)

        gui.uncovered.connect(logic.uncover)
        logic.uncovered.connect(gui.uncover)

        gui.flagged.connect(logic.flag)
        logic.flagged.connect(gui.flag)
        logic.gameOver.connect(gui.showGameOver)

        logic.start(8, 5, 5)
        logic.unlockInput()

        self.logic = logic
        logic.playerConnected.connect(gui.addPlayer)
        logic.playerNameChanged.connect(gui.changePlayerName)
        logic.playerLeft.connect(gui.removePlayer)
        logic.playersTurn.connect(gui.playersTurn)

        logic.listen()

    def restart(self):
        self.logic.start(10, 8, 8)
        self.logic.unlockInput()

    def gameOver(self, won):
        print("Game over", won)
        self.logic.lockInput()
        self.m.gameOver()

    def nameChanged(self, id, name):
        print("name changed", id, name)

    def playerConnected(self, id, ip):
        print("player connected", id, ip)
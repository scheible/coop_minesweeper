from PyQt5.QtWidgets import QMainWindow
from clientGui import ClientGui
from clientLogic import GameClient
from minefieldGui import MinefieldGui


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Death-Match Minesweeper")
        self.setGeometry(50, 50, 500, 500)

        gui = MinefieldGui(self)
        logic = GameClient(self)
        self.m = gui
        self.setCentralWidget(gui)

        logic.gameStarted.connect(gui.reset)

        logic.start(10, 10, 20)


    def restart(self):
        self.logic.start(10, 8, 8)
        self.logic.unlockInput()

    def gameOver(self, won):
        print("Game over", won)
        self.logic.lockInput()

    def nameChanged(self, id, name):
        print("name changed", id, name)

    def playerConnected(self, id, ip):
        print("player connected", id, ip)
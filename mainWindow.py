from PyQt5.QtWidgets import QMainWindow
from clientGui import ClientGui
from clientLogic import GameClient


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Death-Match Minesweeper")
        self.setGeometry(50, 50, 500, 500)

        gui = ClientGui(self)
        logic = GameClient(self)
        self.m = gui
        self.setCentralWidget(gui)

        logic.gameStarted.connect(gui.reset)

        gui.uncovered.connect(logic.uncover)
        gui.flagged.connect(logic.flag)
        logic.uncovered.connect(gui.uncover)

        gui.flagged.connect(logic.flag)
        logic.flagged.connect(gui.flag)
        logic.gameOver.connect(gui.showGameOver)

        logic.unlockInput()

        self.logic = logic
        logic.playerConnected.connect(gui.addPlayer)
        logic.playerNameChanged.connect(gui.changePlayerName)
        logic.playerLeft.connect(gui.removePlayer)
        logic.playersTurn.connect(gui.playersTurn)
        logic.yourTurn.connect(gui.yourTurn)
        logic.disconnected.connect(gui.disconnect)
        logic.connected.connect(gui.connect)
        logic.connecting.connect(gui.connecting)
        logic.minesLeftChanged.connect(gui.showMinesLeft)
        logic.playerScoreChanged.connect(gui.changePlayerScore)
        logic.message.connect(gui.showMessage)

        gui.join.connect(logic.connect)
        gui.leave.connect(logic.leave)
        gui.changeName.connect(logic.changeName)



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
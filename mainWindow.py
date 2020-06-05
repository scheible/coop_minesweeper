from PyQt5.QtWidgets import QMainWindow
from clientLogic import GameClient
from clientGui import ClientGui


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Coop Minesweeper")
        self.setGeometry(50, 50, 500, 500)

        self.gui = ClientGui(self)
        self.logic = GameClient(self)

        self.setCentralWidget(self.gui)

        self.gui.join.connect(self.logic.connect)
        self.gui.leave.connect(self.logic.leave)
        self.gui.changeName.connect(self.logic.changeName)
        self.gui.uncovered.connect(self.logic.uncover)
        self.gui.flagged.connect(self.logic.flag)

        self.logic.yourTurn.connect(self.gui.yourTurn)
        self.logic.disconnected.connect(self.gui.disconnect)
        self.logic.connected.connect(self.gui.connect)
        self.logic.playerConnected.connect(self.gui.addPlayer)
        self.logic.playerNameChanged.connect(self.gui.changePlayerName)
        self.logic.playersTurn.connect(self.gui.playersTurn)
        self.logic.playerScoreChanged.connect(self.gui.changePlayerScore)
        self.logic.playerLeft.connect(self.gui.removePlayer)

        self.logic.message.connect(self.gui.showMessage)
        self.logic.uncovered.connect(self.gui.uncover)
        self.logic.flagged.connect(self.gui.flag)
        self.logic.gameStarted.connect(self.gui.reset)
        self.logic.gameOver.connect(self.gui.showGameover)
        self.logic.minesLeftChanged.connect(self.gui.showMinesLeft)

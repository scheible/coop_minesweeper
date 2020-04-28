from PyQt5.QtCore import QObject, QThread, pyqtSignal
from serverLogic import GameServer
import time


class Timer(QThread):
    expire = pyqtSignal()

    def __init__(self, seconds,  parent=None):
        super(Timer, self).__init__(parent)
        self._seconds = seconds

    def run(self):
        time.sleep(self._seconds)
        self.expire.emit()


class GameConfig():
    def __init__(self, l=""):
        self.loadFromString(l)

    # <label>; <x_size>; <y_size>; <n_mines>; <win_label>; <lose_label>; <t_wait_in_s>
    def loadFromString(self, s):
        fields = s.split(";")
        if len(fields) >= 7 and s[0] != '#':
            self.label = fields[0].strip()
            self.x = int(fields[1])
            self.y = int(fields[2])
            self.nMines = int(fields[3])
            self.nextWin = fields[4].strip()
            self.nextLose = fields[5].strip()
            self.tWait = int(fields[6])


class ServerCli(QObject):
    t = None

    def __init__(self, parent=None):
        super(ServerCli, self).__init__(parent)

        print("Server started")

        server = GameServer(self)
        self.server = server
        self.configList = {}
        self.loadConfig("server.conf")
        self.currentConfig = self.configList[list(self.configList.keys())[0]]

        server.playerConnected.connect(self.onPlayerConnected)
        server.playerNameChanged.connect(self.onPlayerNameChanged)
        server.playerUncovered.connect(self.onPlayerUncover)
        server.playersTurn.connect(self.onPlayersTurn)
        server.playerLeft.connect(self.onPlayerLeft)

        server.gameOver.connect(self.onGameOver)
        server.gameStarted.connect(self.onGameStarted)
        server.minesLeftChanged.connect(self.onMineLeftChanged)

        self.players = {}
        self.restartGame()
        server.listen()

    def loadConfig(self, fileName):
        s = open(fileName).read()
        for l in s.split('\n'):
            gc = GameConfig(l)
            self.configList[gc.label] = gc

    def onGameOver(self, win):
        waitTime = self.currentConfig.tWait

        if (win):
            print("Players WIN")
            self.currentConfig = self.configList[self.currentConfig.nextWin]
        else:
            print("Players LOOSE")
            self.currentConfig = self.configList[self.currentConfig.nextLose]

        global t
        t = Timer(waitTime)
        t.expire.connect(self.restartGame)
        t.start()

    def restartGame(self):
        self.server.start(self.currentConfig.x, self.currentConfig.y, self.currentConfig.nMines)

    def onGameStarted(self, x, y):
        print("started a new game with size", x, y)

    def onMineLeftChanged(self, n):
        print(n, "mines left")

    def onPlayerConnected(self, id, ip):
        print("new player connected:", id, ip)
        self.players[id] = ip

    def onPlayerNameChanged(self, id, name):
        print("player", id, "changed name from", self.players[id], "to", name)
        self.players[id] = name

    def onPlayerUncover(self, id, x, y):
        print("player", self.players[id], "uncovered", x, y)

    def onPlayersTurn(self, id, name):
        print("player", self.players[id], "'s turn")

    def onPlayerLeft(self, id):
        print("player", self.players[id], "left")
        del self.players[id]

from PyQt5.QtCore import pyqtSignal, QObject, QByteArray, QTimer
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket, QAbstractSocket
from multiplayerGameLogic import MultiplayerGameLogic


class PlayerConnection(QObject):
    nameChanged = pyqtSignal(str)
    disconnected = pyqtSignal()
    uncovered = pyqtSignal(int, int)
    flagged = pyqtSignal(int, int)
    scoreChanged = pyqtSignal(int, int)

    def __init__(self, socket: QTcpSocket, id, parent=None):
        super(PlayerConnection, self).__init__(parent)
        self.__playerName = socket.peerAddress().toString()
        self.__socket = socket
        self.__socket.readyRead.connect(self.__onReadReady)
        self.__socket.stateChanged.connect(self.__onStateChange)
        self.__id = id
        self.__score = 0

    def addScore(self, n):
        self.__score += n
        self.scoreChanged.emit(self.__id, self.__score)

    def setScore(self, n):
        self.__score = n
        self.scoreChanged.emit(self.__id, self.__score)

    def getScore(self):
        return self.__score

    def sendMessage(self, msg):
        data = bytearray()
        data += b'MSG'
        data.append(len(msg))
        data += bytearray(msg, 'utf-8')
        self.__socket.write(data)

    def sendMap(self, mapData):
        data = bytearray()
        data += b'MAP'
        data += mapData
        self.__socket.write(data)

    def sendYourTurn(self):
        self.sendTurn(self.__id, self.__playerName)

    def sendTurn(self, id: int, name: str):
        if (id != None):
            data = bytearray()
            if (id == self.__id):
                data += b'YTN'
            else:
                data += b'TRN'
                data.append(id)
            self.__socket.write(data)

    def sendPlayerJoined(self, id):
        data = bytearray(4)
        data[:3] = b'JON'
        data[3] = id
        self.__socket.write(data)

    def sendNameChanged(self, id: int, name: str):
        data = bytearray()
        data += b'HEL'
        data.append(id)
        data.append(len(name))
        data += bytearray(name, 'utf-8')
        self.__socket.write(data)

    def sendLeft(self, id: int):
        data = bytearray()
        data += b'LFT'
        data.append(id)
        self.__socket.write(data)

    def sendPlayerList(self, playerList):
        data = bytearray()
        data += b'PLS'

        for p in playerList:
            data.append(p.getID())
            data.append(p.getScore())
            data.append(len(p.getPlayerName()))
            data += bytearray(p.getPlayerName(), "utf-8")

        data += b'\x00\x00\x00'

        self.__socket.write(data)

    def sendFlag(self, x: int, y: int):
        data = bytearray()
        data += b'FLG'
        data.append(0)
        data.append(x)
        data.append(y)
        self.__socket.write(data)

    def sendUncover(self, x: int, y: int):
        data = bytearray()
        data += b'UCV'
        data.append(0)
        data.append(x)
        data.append(y)
        self.__socket.write(data)

    def sendScore(self, id: int, score: int):
        data = bytearray()
        data += b'SCR'
        data.append(id)
        data.append(score)
        self.__socket.write(data)

    def getPlayerName(self):
        return self.__playerName

    def getIP(self):
        return self.__socket.peerAddress().toString()

    def getID(self):
        return self.__id

    def __onReadReady(self):
        data = self.__socket.readAll()
        self.__parseCommand(data)

    def __onStateChange(self, state):
        if (state == QAbstractSocket.UnconnectedState):
            self.disconnected.emit()

    def __parseCommand(self, command:QByteArray):
        header = command[0:3]

        if (header == b'HEL'):
            self.__helloMessage(command[3:])

        if (header == b'CLK'):
            self.__click(command[3:])

        if (header == b'FLG'):
            self.__flag(command[3:])

        if (header == b'UCV'):
            self.__uncover(command[3:])

    def __helloMessage(self, data: QByteArray):
        s = str(data)[2:-1]
        self.__playerName = s.strip()
        self.nameChanged.emit(self.__playerName)

    def __click(self, data: QByteArray):
        x = int.from_bytes(data[0], "big")
        y = int.from_bytes(data[1], "big")
        self.clicked.emit(x, y)

    def __flag(self, data: QByteArray):
        x = int.from_bytes(data[0], "big")
        y = int.from_bytes(data[1], "big")
        self.flagged.emit(x, y)

    def __uncover(self, data: QByteArray):
        x = int.from_bytes(data[0], "big")
        y = int.from_bytes(data[1], "big")
        self.uncovered.emit(x, y)


class GameServer(MultiplayerGameLogic):
    mapChanged = pyqtSignal(bytearray)

    def __init__(self, parent=None):
        super(GameServer, self).__init__(parent)
        self._players = []
        self._idCounter = 0

    def listen(self):
        self.__server = QTcpServer()
        self.__server.listen(QHostAddress.AnyIPv4, 4444)
        self.__server.newConnection.connect(self.onNewConnection)

    def onNewConnection(self):
        socket = self.__server.nextPendingConnection()
        player = PlayerConnection(socket, self._idCounter)
        self._idCounter += 1

        player.disconnected.connect(self._onPlayerDisconnect)
        player.nameChanged.connect(self._onPlayerNameChanged)
        player.uncovered.connect(self._onPlayerUncover)
        player.flagged.connect(self._onPlayerFlagged)
        player.scoreChanged.connect(self._onPlayerScoreChanged)

        player.sendMap(self._encodeMineField())
        player.sendPlayerList(self._players)
        self._players.append(player)

        self.playerConnected.connect(player.sendPlayerJoined)
        self.playerLeft.connect(player.sendLeft)
        self.playerNameChanged.connect(player.sendNameChanged)
        self.playersTurn.connect(player.sendTurn)
        self.flagged.connect(player.sendFlag)
        self.uncovered.connect(player.sendUncover)
        self.mapChanged.connect(player.sendMap)
        self.playerScoreChanged.connect(player.sendScore)
        self.message.connect(player.sendMessage)

        self.playerConnected.emit(player.getID(), player.getIP())

        return player

    def _onPlayerFlagged(self, x, y):
        pass

    def _onPlayerScoreChanged(self, score):
        player = self.sender()
        self.playerScoreChanged.emit(player.getID(), player.getScore())

    def _onPlayerUncover(self, x, y):
        pass

    def _onPlayerDisconnect(self):
        player = self.sender()
        self._players.remove(player)
        self.playerLeft.emit(player.getID())

    def _onPlayerNameChanged(self, name):
        player = self.sender()
        self.playerNameChanged.emit(player.getID(), name)


class CoopServer(GameServer):

    def __init__(self, parent=None):
        super(CoopServer, self).__init__(parent)
        self._currentPlayer = None
        self._nextPlayerTimer = QTimer()
        self._nextPlayerTimer.timeout.connect(self.nextPlayer)

    def onNewConnection(self):
        player = super(CoopServer, self).onNewConnection()
        if (self._currentPlayer == None):
            self.setCurrentPlayer(player)
        else:
            player.sendTurn(self._currentPlayer.getID(), "")

    def setCurrentPlayer(self, player):
        self._currentPlayer = player
        if (not self._gameOver):
            self.playersTurn.emit(player.getID(), player.getPlayerName())
            self._nextPlayerTimer.stop()
            self._nextPlayerTimer.start(10000)

    def nextPlayer(self):
        if len(self._players) > 0:
            if self._currentPlayer is None or not self._currentPlayer in self._players:
                if len(self._players) > 0:
                    self.setCurrentPlayer(self._players[0])
            else:
                idx = self._players.index(self._currentPlayer)
                newIdx = (idx+1) % len(self._players)
                self.setCurrentPlayer(self._players[newIdx])
        else:
            self._currentPlayer = None

    def start(self, xSize: int, ySize: int, nMines: int):
        super(GameServer, self).start(xSize, ySize, nMines)
        self.mapChanged.emit(self._encodeMineField())
        self.nextPlayer()
        self._gameOver = False

    def _onPlayerFlagged(self, x, y):
        player = self.sender()
        if player == self._currentPlayer:
            self.flag(x, y)

    def _onPlayerUncover(self, x, y):
        player = self.sender()
        if player == self._currentPlayer:
            self.uncover(x, y)
            self.nextPlayer()

    def _onPlayerDisconnect(self):
        player = self.sender()
        self._players.remove(player)
        self.playerLeft.emit(player.getID())
        if self._currentPlayer == player:
            self.nextPlayer()

    def _onPlayerNameChanged(self, name):
        player = self.sender()
        self.playerNameChanged.emit(player.getID(), name)

        # reset the current player, so that the new name
        # gets propageted in this event
        if (self._currentPlayer == player):
            self.setCurrentPlayer(player)


class DeathMatchServer(GameServer):

    def __init__(self, parent=None):
        super(DeathMatchServer, self).__init__(parent)
        self._gameOver = True
        self._startCounter = 0
        self._countDown = QTimer()
        self._countDown.timeout.connect(self.gameTicker)

    def gameTicker(self):
        self._startCounter -= 1
        self.message.emit("Start in " + str(self._startCounter-1))

        if (self._startCounter == 1):
            self.message.emit("START!!")

        if (self._startCounter == 0):
            self._countDown.stop()
            self.unlockInput()
            self.message.emit("")

    def start(self, xSize: int, ySize: int, nMines: int):
        super(GameServer, self).start(xSize, ySize, nMines)
        self.mapChanged.emit(self._encodeMineField())
        self._gameOver = False

        for p in self._players:
            p.setScore(0)
            p.sendYourTurn()

        self.lockInput()
        self._startCounter = 7
        self.message.emit("Start in " + str(self._startCounter-1))
        self._countDown.start(1000)

    def _onPlayerUncover(self, x, y):
        success = self.uncover(x, y)
        print("success", success)
        player = self.sender()
        if success >= 0:
            if success < 9:
                player.addScore(1)
            else:
                player.setScore(0)

    def _onPlayerFlagged(self, x, y):
        self.flag(x, y)

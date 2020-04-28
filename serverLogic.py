from PyQt5.QtCore import pyqtSignal, QObject, QByteArray
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket, QAbstractSocket
from multiplayerGameLogic import MultiplayerGameLogic


class PlayerConnection(QObject):
    nameChanged = pyqtSignal(str)
    disconnected = pyqtSignal()
    uncovered = pyqtSignal(int, int)
    flagged = pyqtSignal(int, int)

    def __init__(self, socket: QTcpSocket, id, parent=None):
        super(PlayerConnection, self).__init__(parent)
        self.__playerName = socket.peerAddress().toString()
        self.__socket = socket
        self.__socket.readyRead.connect(self.__onReadReady)
        self.__socket.stateChanged.connect(self.__onStateChange)
        self.__id = id
        self.__score = 0

    def sendMap(self, mapData):
        data = bytearray()
        data += b'MAP'
        data += mapData
        self.__socket.write(data)

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
        self._currentPlayer = None

    def listen(self):
        self.__server = QTcpServer()
        self.__server.listen(QHostAddress.AnyIPv4, 4444)
        self.__server.newConnection.connect(self.onNewConnection)

    def setCurrentPlayer(self, player):
        self._currentPlayer = player
        if (not self._gameOver):
            self.playersTurn.emit(player.getID(), player.getPlayerName())

    def nextPlayer(self):
        if len(self._players) > 0:
            if self._currentPlayer is None or not self._currentPlayer in self._players:
                print("init turn to player 0")
                if len(self._players) > 0:
                    self.setCurrentPlayer(self._players[0])
            else:
                idx = self._players.index(self._currentPlayer)
                newIdx = (idx+1) % len(self._players)
                self.setCurrentPlayer(self._players[newIdx])
                print("changing from player", idx, "to player", newIdx)
        else:
            print("setting current player to none")
            self._currentPlayer = None

    def start(self, xSize: int, ySize: int, nMines: int):
        super(GameServer, self).start(xSize, ySize, nMines)
        self.mapChanged.emit(self._encodeMineField())
        self.nextPlayer()
        self._gameOver = False

    def onNewConnection(self):
        socket = self.__server.nextPendingConnection()
        player = PlayerConnection(socket, self._idCounter)
        self._idCounter += 1

        player.disconnected.connect(self._onPlayerDisconnect)
        player.nameChanged.connect(self._onPlayerNameChanged)
        player.uncovered.connect(self._onPlayerUncover)
        player.flagged.connect(self._onPlayerFlagged)

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

        self.playerConnected.emit(player.getID(), player.getIP())

        if (self._currentPlayer == None):
            self.setCurrentPlayer(player)
        else:
            player.sendTurn(self._currentPlayer.getID(), "")

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



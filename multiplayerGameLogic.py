from PyQt5.QtCore import pyqtSignal, QObject, QByteArray
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket, QAbstractSocket
from gameLogic import GameLogic, Field


class MultiplayerGameLogic(GameLogic):
    playerConnected = pyqtSignal(int, str)
    playerNameChanged = pyqtSignal(int, str)
    playerUncovered = pyqtSignal(int, int, int)
    playersTurn = pyqtSignal(int, str)
    playerScoreChanged = pyqtSignal(int, int)
    playerLeft = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MultiplayerGameLogic, self).__init__(parent)

    def _encodeMineField(self):
        c = 0
        totalBytes = int(((self._xSize * self._ySize)+1) / 2)
        data = bytearray(totalBytes)
        for y in range(self._ySize):
            for x in range(self._xSize):
                bytePos = int(c / 2)
                bitPos = (c % 2) * 4
                val = self._fields[x][y].encode()
                data[bytePos] = data[bytePos] | (val << bitPos)
                c += 1

        tData = bytearray()
        tData.append(self._xSize)
        tData.append(self._ySize)
        tData += data

        return tData

    def _decodeMineField(self, data):
        xSize = int.from_bytes(data[0], 'big')
        ySize = int.from_bytes(data[1], 'big')

        self._initField(xSize, ySize)
        self.gameStarted.emit(xSize, ySize)

        nMines = 0
        totalMines = xSize * ySize
        for i in range(0, totalMines):
            bytePos = int(i / 2)
            bitPos = int((i % 2) * 4)
            b = int.from_bytes(data[bytePos+2], 'big')
            val = (b >> bitPos) & 0xF

            x = int(i % xSize)
            y = int(i / xSize)
            f = self._fields[x][y]
            f.decode(val)

            if f.isMine():
                nMines += 1

        self._markFields()
        self._nMines = nMines
        self._resyncGui()


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


class GameClient(MultiplayerGameLogic):
    yourTurn = pyqtSignal()
    disconnected = pyqtSignal()
    connected = pyqtSignal()
    connecting = pyqtSignal()

    def __init__(self, parent=None):
        super(GameClient, self).__init__(parent)
        self.__socket = QTcpSocket()
        self.__socket.connected.connect(self.onConnect)
        self.__socket.readyRead.connect(self.readyRead)
        self.__socket.disconnected.connect(self.disconnected.emit)
        self.__socket.stateChanged.connect(self._onStateChanged)
        self._name = "<no name>"

    def _onStateChanged(self, state):
        if state == QTcpSocket.UnconnectedState:
            self.disconnected.emit()

    def flag(self, x: int, y: int):
        data = bytearray()
        data += b'FLG'
        data.append(x)
        data.append(y)
        self.__socket.write(data)

    def uncover(self, x: int, y: int, auto: bool = False):
        # if the field was automatically uncovered by the logic
        # we do not need to send that to the server. The server
        # logic will also automatically uncover these fields
        if auto:
            return
        data = bytearray()
        data += b'UCV'
        data.append(x)
        data.append(y)
        self.__socket.write(data)

    def readyRead(self):
        data = self.__socket.readAll()
        print(data)
        self._parsePacket(data)

    def onConnect(self):
        self.connected.emit()
        self.changeName(self._name)

    def connect(self, ip, port, name):
        if self.__socket.state() == QTcpSocket.UnconnectedState:
            self._name = name
            self.__socket.connectToHost(ip, port)
            self.connecting.emit()

    def leave(self):
        self.__socket.close()
        self.disconnected.emit()

    def changeName(self, name):
        self._name = name
        data = bytearray()
        data += b'HEL'
        data += bytearray(self._name, 'utf-8')
        self.__socket.write(data)

    def rcvMAP(self, data):
        xSize = int.from_bytes(data[0], 'big')
        ySize = int.from_bytes(data[1], 'big')
        total = int(((xSize * ySize) + 1) / 2)

        self._decodeMineField(data)
        self.unlockInput()

        return total+2

    def rcvPLS(self, data):
        print("received player list")
        offset = 0

        while (len(data) >= 3):
            if (data[:3] == b'\x00\x00\x00'):
                offset += 3
                break
            id = int.from_bytes(data[0], "big")
            l = int.from_bytes(data[1], "big")
            name = bytearray(data[2:l+2])
            data = data[l+2:]
            offset += 2+l
            self.playerConnected.emit(id, name.decode('utf-8'))
            self.playerNameChanged.emit(id, name.decode('utf-8'))
        return offset

    def rcvJON(self, data):
        print("received join", data)
        self.playerConnected.emit(int.from_bytes(data[0], "big"), "new player")
        return 1

    def rcvYTN(self, data):
        print("YOUr TURN")
        self.yourTurn.emit()
        return 0

    def rcvTRN(self, data):
        id = int.from_bytes(data[0], "big")
        self.playersTurn.emit(id, "no name")
        return 1

    def rcvHEL(self, data):
        print("received HEL")
        id = int.from_bytes(data[0], "big")
        l = int.from_bytes(data[1], "big")
        name = bytearray(data[2:l+2])
        self.playerNameChanged.emit(id, name.decode('utf-8'))
        return l+2

    def rcvLFT(self, data):
        id = int.from_bytes(data[0], 'big')
        self.playerLeft.emit(id)
        return 1

    def rcvFLG(self, data):
        id = int.from_bytes(data[0], 'big')
        x = int.from_bytes(data[1], 'big')
        y = int.from_bytes(data[2], 'big')
        super(GameClient, self).flag(x, y)
        return 3

    def rcvUCV(self, data):
        id = int.from_bytes(data[0], 'big')
        x = int.from_bytes(data[1], 'big')
        y = int.from_bytes(data[2], 'big')
        super(GameClient, self).uncover(x, y)
        return 3

    def _parsePacket(self, data):
        while (len(data) >= 3):
            header = data[:3]
            data = data[3:]
            if (header == b'MAP'):
                offset = self.rcvMAP(data)
                data = data[offset:]

            elif (header == b'PLS'):
                offset = self.rcvPLS(data)
                data = data[offset:]

            elif (header == b'JON'):
                self.rcvJON(data)
                data = data[1:]

            elif (header == b'YTN'):
                self.rcvYTN(None)

            elif (header == b'TRN'):
                offset = self.rcvTRN(data)
                data = data[offset:]

            elif (header == b'HEL'):
                offset = self.rcvHEL(data)
                data = data[offset:]

            elif (header == b'LFT'):
                offset = self.rcvLFT(data)
                data = data[offset:]

            elif (header == b'FLG'):
                offset = self.rcvFLG(data)
                data = data[offset:]

            elif (header == b'UCV'):
                offset = self.rcvUCV(data)
                data = data[offset:]

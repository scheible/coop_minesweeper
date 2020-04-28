from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QByteArray, QModelIndex, QAbstractTableModel
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
import random, time

class PlayerList(QAbstractTableModel):
    def __init__(self, parent=None):
        super(PlayerList, self).__init__(parent)

        self.__connectedPlayers = []

    def addPlayer(self, player):
        self.__connectedPlayers.append(player)
        i = self.index(0, 0, QModelIndex())
        j = self.index(0, 2, QModelIndex())
        self.dataChanged.emit(i, j)

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__connectedPlayers)

    def columnCount(self, parent: QModelIndex) -> int:
        return 2

    def data(self, index: QModelIndex, role):
        if (role == Qt.DisplayRole):
            col = index.column()
            row = index.row()
            if (col == 0):
                return self.__connectedPlayers[col].getPlayerName()
            else:
                return "0"
        else:
            return None

    def headerData(self, section, orientation, role):
        headers = ['Name', 'Score']

        if (role == Qt.DisplayRole):
            if (orientation == 1):
                if (section < len(headers)):
                    return headers[section]
                else:
                    return "-"
            elif (orientation == 2):
                return str(section + 1)

class PlayerConnection(QObject):
    nameChanged = pyqtSignal(str)
    disconnected = pyqtSignal()

    def __init__(self, socket: QTcpSocket, parent=None):
        super(PlayerConnection, self).__init__(parent)
        self.__playerName = socket.peerAddress().toString()
        self.__socket = socket
        self.__socket.readyRead.connect(self.__onReadReady)
        self.__socket.stateChanged.connect(self.__onStateChange)

    def sendMap(self):
        self.__socket.write(b'MAP ')

    def getPlayerName(self):
        return self.__playerName

    def getIP(self):
        return self.__socket.peerAddress().toString()

    def __onReadReady(self):
        data = self.__socket.readAll()
        self.__parseCommand(data)

    def __onStateChange(self, state):
        if (state == QAbstractSocket.UnconnectedState):
            self.disconnected.emit()

    def __parseCommand(self, command:QByteArray):
        header = command[0:3]

        if (header == b'HEL'):
            self.__helloMessage(command[4:])

    def __helloMessage(self, data: QByteArray):
        s = str(data)[2:-1]
        self.__playerName = s.strip()
        self.nameChanged.emit(self.__playerName)

class GameServer(QObject):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super(GameServer, self).__init__(parent)
        self.__server = QTcpServer()
        self.__server.listen(QHostAddress.AnyIPv4, 4444)
        self.__server.newConnection.connect(self.onNewConnection)
        self.players = PlayerList()

    def onNewConnection(self):
        socket = self.__server.nextPendingConnection()
        player = PlayerConnection(socket)
        self.players.addPlayer(player)
        player.disconnected.connect(self.__onPlayerDisconnect)
        player.nameChanged.connect(self.__onPlayerNameChanged)
        print(player.getPlayerName(), "connected")
        player.sendMap()
        self.changed.emit()


    def __onPlayerNameChanged(self, name):
        player = self.sender()
        ip = player.getIP()
        print(ip, "changed name to", name)
        self.changed.emit()

    def __onPlayerDisconnect(self):
        player: PlayerConnection = self.sender()
        print(player.getPlayerName(), "left")
        #self.__players.remove(player)


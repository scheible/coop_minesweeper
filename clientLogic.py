from PyQt5.QtCore import pyqtSignal
from PyQt5.QtNetwork import QTcpSocket
from multiplayerGameLogic import MultiplayerGameLogic


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
        offset = 0

        while (len(data) >= 3):
            if (data[:3] == b'\x00\x00\x00'):
                offset += 3
                break
            id = int.from_bytes(data[0], "big")
            score = int.from_bytes(data[1], "big")
            l = int.from_bytes(data[2], "big")
            name = bytearray(data[3:l+3])
            data = data[l+3:]
            offset += 3+l
            self.playerConnected.emit(id, name.decode('utf-8'))
            self.playerNameChanged.emit(id, name.decode('utf-8'))
            self.playerScoreChanged.emit(id, score)
        return offset

    def rcvJON(self, data):
        self.playerConnected.emit(int.from_bytes(data[0], "big"), "new player")
        return 1

    def rcvYTN(self, data):
        self.yourTurn.emit()
        return 0

    def rcvTRN(self, data):
        id = int.from_bytes(data[0], "big")
        self.playersTurn.emit(id, "no name")
        return 1

    def rcvHEL(self, data):
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

    def rcvSCR(self, data):
        id = int.from_bytes(data[0], 'big')
        score = int.from_bytes(data[1], 'big')
        self.playerScoreChanged.emit(id, score)
        return 2

    def rcvMSG(self, data):
        l = int.from_bytes(data[0], 'big')
        msg = bytearray(data[1:l+1])
        self.message.emit(msg.decode('utf-8'))
        return l+1

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

            elif (header == b'SCR'):
                offset = self.rcvSCR(data)
                data = data[offset:]

            elif (header == b'MSG'):
                offset = self.rcvMSG(data)
                data = data[offset:]

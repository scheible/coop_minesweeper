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
    message = pyqtSignal(str)

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
        self.minesLeftChanged.emit(nMines)
        self._resyncGui()



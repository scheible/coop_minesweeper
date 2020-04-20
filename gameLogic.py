from PyQt5.QtCore import QObject, pyqtSignal
import random


class Field(QObject):
    def __init__(self, x, y, parent=None):
        super(Field, self).__init__(parent)
        self._isFlagged = False
        self._isMine = False
        self._isCovered = True
        self._nNeighbours = 0
        self.x = x
        self.y = y

    def encode(self):
        val = 0
        val |= (int(self._isMine)) << 3
        val |= (int(self._isCovered)) << 2
        val |= (int(self._isFlagged)) << 1

        return val

    def decode(self, val):
        self._isMine = (val & 0b1000) != 0
        self._isCovered = (val & 0b0100) != 0
        self._isFlagged = (val & 0b0010) != 0

    def setNeighbours(self, n: int):
        self._nNeighbours = n

    def isFlagged(self):
        return self._isFlagged

    def isMine(self):
        return self._isMine

    def setMine(self):
        self._isMine = True

    def flag(self):
        # Can only flag mines that are not uncovered yet
        if self._isCovered:
            self._isFlagged = not self._isFlagged
        return self._isFlagged

    def isUncovered(self):
        return not self._isCovered

    def getState(self):
        if self._isMine:
            return 9
        else:
            return self._nNeighbours

    def uncover(self):
        if not self._isFlagged and self._isCovered:
            self._isCovered = False
            return self.getState()
        return -1


class GameLogic(QObject):
    uncovered = pyqtSignal(int, int, int, bool)
    flagged = pyqtSignal(int, int, bool)
    gameStarted = pyqtSignal(int, int)
    gameOver = pyqtSignal(bool)
    inputLocked = pyqtSignal(bool)
    minesLeftChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GameLogic, self).__init__(parent)
        self._fields = []
        self._xSize = 0
        self._ySize = 0
        self._nMines = 0
        self._inputLocked = True
        self._gameOver = False

    def lockInput(self):
        self._inputLocked = True
        self.inputLocked.emit(True)

    def unlockInput(self):
        self._inputLocked = False
        self.inputLocked.emit(False)

    def flag(self, x: int, y: int):
        if self._inputLocked:
            return

        field = self._fields[x][y]
        isFlagged = field.flag()
        if isFlagged:
            self._minesFlagged += 1
        else:
            self._minesFlagged -= 1

        self.minesLeftChanged.emit(self.getMinesLeft())
        self.flagged.emit(x, y, isFlagged)

    def getMinesLeft(self):
        return self._nMines - self._minesFlagged

    def _isGameWon(self):
        if self._uncovered >= (self._xSize * self._ySize) - self._nMines:
            return True
        else:
            return False

    def start(self, xSize: int, ySize: int, nMines: int):
        self._nMines = nMines
        self._initField(xSize, ySize)
        self._placeMines()
        self._markFields()
        self._gameOver = False
        self.gameStarted.emit(xSize, ySize)
        self.unlockInput()

    def _initField(self, xSize, ySize):
        self._fields = []

        self._minesFlagged = 0
        self._uncovered = 0

        for x in range(0, xSize):
            self._fields.append([None] * ySize)
            for y in range(0, ySize):
                self._fields[x][y] = Field(x, y)

        self._xSize = xSize
        self._ySize = ySize

    def _placeMines(self):
        minesPlaced = 0

        while (minesPlaced < self._nMines):
            x = random.randint(0, self._xSize - 1)
            y = random.randint(0, self._ySize - 1)

            if (not self._fields[x][y].isMine()):
                self._fields[x][y].setMine()
                minesPlaced += 1

    def _markFields(self):
        for row in self._fields:
            for f in row:
                n = self._getNeighbourCount(f)
                f.setNeighbours(n)

    def _getNeighbourCount(self, field):
        neighbours = self._getNeighbourFields(field)
        n = 0
        for neighbour in neighbours:
            if neighbour.isMine():
                n += 1
        return n

    def _getNeighbourFields(self, field):
        xStart = max(0, field.x - 1)
        xEnd = min(self._xSize - 1, field.x + 1)
        yStart = max(0, field.y - 1)
        yEnd = min(self._ySize - 1, field.y + 1)
        nFields = []
        for x in range(xStart, xEnd + 1):
            for y in range(yStart, yEnd + 1):
                if not (x == field.x and y == field.y):
                    nFields.append(self._fields[x][y])
        return nFields

    def uncover(self, x: int, y: int, auto: bool = False):
        if self._inputLocked:
            return

        field = self._fields[x][y]
        state = field.uncover()
        if state >= 0:
            self._uncovered += 1
            if state == 0:
                self._uncoverNext(field)
            elif state == 9:
                self._gameOver = True
                self.lockInput()
                self.gameOver.emit(False)
            elif self._isGameWon():
                self._gameOver = True
                self.lockInput()
                self.gameOver.emit(True)

            self.uncovered.emit(x, y, state, auto)

    def _uncoverNext(self, field):
        next = self._getNeighbourFields(field)
        for n in next:
            self.uncover(n.x, n.y, True)

    def _resyncGui(self):
        for a in self._fields:
            for field in a:
                if field.isFlagged():
                    self.flagged.emit(field.x, field.y, True)
                if field.isUncovered():
                    self.uncovered.emit(field.x, field.y, field.getState(), True)

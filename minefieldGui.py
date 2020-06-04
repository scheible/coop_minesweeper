from PyQt5.QtWidgets import QWidget, QGridLayout, QStackedLayout, QPushButton, QSizePolicy, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class MineButton(QPushButton):
    flagged = pyqtSignal()
    uncovered = pyqtSignal()

    def __init__(self, x: int, y: int, parent=None):
        super(MineButton, self).__init__(parent)
        self.__isUncoverable = True
        self.__isFlaggable = True
        self.x = x
        self.y = y

    # Override the mouse press events
    # We only want the uncover and flag
    # events to be passed on
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and self.__isFlaggable:
            self.flagged.emit()
            print(self.x, self.y)

        elif event.button() == Qt.LeftButton and self.__isUncoverable:
            self.uncovered.emit()

    def flag(self):
        self.__isUncoverable = False
        self.setIcon(QIcon("assets/flag.svg"))

    def unflag(self):
        self.__isUncoverable = True
        self.setIcon(QIcon())

    def mine(self):
        self.__isUncoverable = False
        self.__isFlaggable = False
        self.setStyleSheet("background-color: #767676; border-style: outset; border-color: #A1A1A1; border-width: 1px")
        self.setIcon(QIcon('assets/mine.svg'))

    def number(self, n: int):
        assets = ['',
                  'assets/1.svg',
                  'assets/2.svg',
                  'assets/3.svg',
                  'assets/4.svg',
                  'assets/5.svg',
                  'assets/6.svg',
                  'assets/7.svg',
                  'assets/8.svg']
        if (n < 0 or n > 8):
            return

        self.__isUncoverable = False
        self.__isFlaggable = False
        self.setStyleSheet("background-color: #767676; border-style: outset; border-color: #A1A1A1; border-width: 1px")
        self.setIcon(QIcon(assets[n]))
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


class MinefieldGui(QWidget):
    uncovered = pyqtSignal(int, int)
    flagged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(MinefieldGui, self).__init__(parent)
        self._createLayout()

    def _createLayout(self):
        self._layout = QVBoxLayout()
        self._leftLabel = QLabel(self)
        self._layout.addWidget(self._leftLabel)

        self._innerFieldLayout = QGridLayout()
        self._innerFieldLayout.setHorizontalSpacing(0)
        self._innerFieldLayout.setVerticalSpacing(0)
        self._layout.addLayout(self._innerFieldLayout)

        self.setLayout(self._layout)

    def showMinesLeft(self, nMines):
        self._leftLabel.setText("Mines Left: " + str(nMines))

    def uncover(self, x: int, y: int, state):
        mb = self.__getMineButton(x, y)
        if mb is None:
            pass
            #TODO: throw exception
        else:
            if (state > 8):
                mb.mine()
            else:
                mb.number(state)

    def flag(self, x: int, y: int, flagged: bool):
        mb = self.__getMineButton(x, y)
        if mb is None:
            pass
            # TODO: later throw an exception here
        else:
            if flagged:
                mb.flag()
            else:
                mb.unflag()

    def __deleteAllMineButtons(self):
        layout = self._innerFieldLayout

        if (layout != None):
            item = layout.takeAt(0)
            while item != None:
                layout.removeItem(item)
                item.widget().deleteLater()
                item = layout.takeAt(0)

    def reset(self, xSize: int, ySize: int):
        self.__deleteAllMineButtons()

        for x in range(0, xSize):
            for y in range(0, ySize):
                b = MineButton(x, y, self)
                b.uncovered.connect(self.__onMinebuttonUncover)
                b.flagged.connect(self.__onMinebuttonFlag)
                b.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
                b.setMinimumSize(50, 50)
                self._innerFieldLayout.addWidget(b, y, x) # the position is referred to as (row, column) -> (y, x)

    def __getMineButton(self, x: int, y: int):
        l: QGridLayout = self._innerFieldLayout
        b: MineButton = l.itemAtPosition(y, x).widget() # (y, x) corresponds to row and column
        return b

    def __onMinebuttonUncover(self):
        self.uncovered.emit(self.sender().x, self.sender().y)

    def __onMinebuttonFlag(self):
        self.flagged.emit(self.sender().x, self.sender().y)

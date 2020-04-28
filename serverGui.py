from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLineEdit, QSpacerItem
from PyQt5.QtCore import pyqtSignal
from multiplayerControlsGui import MultiplayerControlsGui


class ServerControlWidget(QWidget):
    start = pyqtSignal(int, int, int)
    stop = pyqtSignal()
    kickPlayer = pyqtSignal(int)

    def __init__(self, parent=None):
        super(ServerControlWidget, self).__init__(parent)

        self._layout1 = QHBoxLayout()
        self._btnStart = QPushButton("Start", self)
        self._btnStart.setMaximumWidth(100)
        self._layout1.addWidget(self._btnStart)
        self._txt_xSize = QLineEdit(self)
        self._txt_ySize = QLineEdit(self)
        self._txt_nMines = QLineEdit(self)
        self._txt_xSize.setMaximumWidth(50)
        self._txt_ySize.setMaximumWidth(50)
        self._txt_nMines.setMaximumWidth(50)
        self._txt_xSize.setPlaceholderText("X Size")
        self._txt_ySize.setPlaceholderText("Y Size")
        self._txt_nMines.setPlaceholderText("Mines")
        self._layout1.addWidget(self._txt_xSize)
        self._layout1.addWidget(self._txt_ySize)
        self._layout1.addWidget(self._txt_nMines)
        self._layout1.addStretch()

        self._layout2 = QHBoxLayout()
        self._btnKick = QPushButton("Kick", self)
        self._btnKick.setMaximumWidth(100)
        self._txtKick = QLineEdit(self)
        self._txtKick.setMaximumWidth(50)
        self._txtKick.setPlaceholderText("ID")
        self._layout2.addWidget(self._btnKick)
        self._layout2.addWidget(self._txtKick)
        self._layout2.addStretch()

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addLayout(self._layout1)
        self._layout.addLayout(self._layout2)
        self._layout.addStretch()

        self._btnStart.clicked.connect(self.__onStartClick)
        self._btnKick.clicked.connect(self.__onKickClick)

    def __onStartClick(self):
        xSize = int(self._txt_xSize.text())
        ySize = int(self._txt_ySize.text())
        nMines = int(self._txt_nMines.text())
        self.start.emit(xSize, ySize, nMines)

    def __onKickClick(self):
        id = int(self._txt_nMines.text())
        self.kickPlayer.emit(id)


class ServerGui(MultiplayerControlsGui):
    start = pyqtSignal(int, int, int)
    stop = pyqtSignal()
    kickPlayer = pyqtSignal(int)

    def __init__(self, parent=None):
        super(ServerGui, self).__init__(parent)

    def _createLayout(self):
        self._headerLayout = QHBoxLayout()

        super(ServerGui, self)._createLayout()

        # remove all the old layout
        for i in range(0, 2):
            i = self._mainLayout.takeAt(0)
            self._mainLayout.removeItem(i)

        # reassemble new
        self._mainLayout.addLayout(self._headerLayout)
        self._mainLayout.addLayout(self._layout)

        self._headerLayout.addLayout(self._mpLayout)
        self._srvCtrl = ServerControlWidget(self)
        self._headerLayout.addWidget(self._srvCtrl)

        self._srvCtrl.start.connect(self.start.emit)
        self._srvCtrl.kickPlayer.connect(self.kickPlayer.emit)



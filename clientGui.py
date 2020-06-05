from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal
from multiplayerControlsGui import MultiplayerControlsGui
from minefieldGui import MinefieldGui

class ClientControlWidget(QWidget):
    connect = pyqtSignal()
    changeName = pyqtSignal()

    def __init__(self, parent=None):
        super(ClientControlWidget, self).__init__(parent)
        self._layout1 = QHBoxLayout()
        self.btnJoin = QPushButton("Join", self)
        self.btnJoin.setMinimumWidth(130)
        self._layout1.addWidget(self.btnJoin)
        self.txt_serverIp = QLineEdit(self)
        self.txt_serverPort = QLineEdit(self)
        self.txt_serverIp.setMaximumWidth(130)
        self.txt_serverPort.setMaximumWidth(50)
        self.txt_serverIp.setPlaceholderText("Server IP")
        self.txt_serverPort.setPlaceholderText("Port")
        self.txt_serverPort.setText("4444")
        self._layout1.addWidget(self.txt_serverIp)
        self._layout1.addWidget(self.txt_serverPort)
        self._layout1.addStretch()

        self._layout2 = QHBoxLayout()
        self.btnChgName = QPushButton("Change Name", self)
        self.btnChgName.setMinimumWidth(130)
        self.btnChgName.setEnabled(False)
        self.txtName = QLineEdit(self)
        self.txtName.setMinimumWidth(150)
        self.txtName.setPlaceholderText("Name")
        self.txtName.setText("Horst")
        self._layout2.addWidget(self.btnChgName)
        self._layout2.addWidget(self.txtName)
        self._layout2.addStretch()

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addLayout(self._layout1)
        self._layout.addLayout(self._layout2)
        self._layout.addStretch()

        self.btnJoin.clicked.connect(self.connect.emit)
        self.btnChgName.clicked.connect(self.changeName.emit)


class ClientGui(QWidget):
    join = pyqtSignal(str, int, str)
    leave = pyqtSignal()
    changeName = pyqtSignal(str)

    uncovered = pyqtSignal(int, int)
    flagged = pyqtSignal(int, int)


    def __init__(self, parent=None):
        super(ClientGui, self).__init__(parent)

        self._cltCtrl = ClientControlWidget(self)
        self._mineField = MinefieldGui(self)
        self._mulitplayerControls = MultiplayerControlsGui(self)

        self._mineField.uncovered.connect(self.uncovered.emit)
        self._mineField.flagged.connect(self.flagged.emit)

        self._cltCtrl.changeName.connect(self._onChangeName)
        self._cltCtrl.connect.connect(self._onJoin)

        self._createLayout()

    def _createLayout(self):
        self._headerLayout = QHBoxLayout()

        self._headerLayout.addWidget(self._mulitplayerControls)
        self._headerLayout.addWidget(self._cltCtrl)
        self._mainLayout = QVBoxLayout()
        self._mainLayout.addLayout(self._headerLayout)
        self._mainLayout.addWidget(self._mineField)

        self.setLayout(self._mainLayout)

    def connecting(self):
        self._cltCtrl.btnChgName.setEnabled(False)
        self._cltCtrl.btnJoin.setEnabled(False)
        self._cltCtrl.txt_serverIp.setEnabled(False)
        self._cltCtrl.txt_serverPort.setEnabled(False)

    def disconnect(self):
        self._cltCtrl.btnChgName.setEnabled(False)
        self._cltCtrl.btnJoin.setEnabled(True)
        self._cltCtrl.btnJoin.setText("Join")
        self._cltCtrl.txt_serverIp.setEnabled(True)
        self._cltCtrl.txt_serverPort.setEnabled(True)
        self._mulitplayerControls.clearPlayerList()
        self._mineField.reset(0, 0)
        self.showMinesLeft(0)

    def connect(self):
        self._cltCtrl.btnJoin.setEnabled(True)
        self._cltCtrl.btnChgName.setEnabled(True)
        self._cltCtrl.btnJoin.setText("Leave")
        self._cltCtrl.txt_serverIp.setEnabled(False)
        self._cltCtrl.txt_serverPort.setEnabled(False)

    def _onChangeName(self):
        self.changeName.emit(self._cltCtrl.txtName.text())

    def _onJoin(self):
        if self._cltCtrl.btnJoin.text() == "Join":
            try:
                ip = self._cltCtrl.txt_serverIp.text()
                port = int(self._cltCtrl.txt_serverPort.text())
                name = self._cltCtrl.txtName.text()

                self.join.emit(ip, port, name)
            except:
                pass
        else:
            self.leave.emit()

    def addPlayer(self, id: int, ip: str):
        self._mulitplayerControls.addPlayer(id, ip)

    def removePlayer(self, id: int):
        self._mulitplayerControls.removePlayer(id)

    def changePlayerName(self, id: int, name: str):
        self._mulitplayerControls.changePlayerName(id, name)

    def changePlayerScore(self, id: int, score: int):
        self._mulitplayerControls.changePlayerScore(id, score)

    def playersTurn(self, id: int, name: str):
        self._mulitplayerControls.playersTurn(id, name)

    def yourTurn(self):
        self._mulitplayerControls.yourTurn()

    def uncover(self, x: int, y: int, state: int):
        self._mineField.uncover(x, y, state)

    def flag(self, x: int, y: int, flagged: bool):
        self._mineField.flag(x, y, flagged)

    def reset(self, xSize: int, ySize: int):
        self._mineField.reset(xSize, ySize)

    def showMinesLeft(self, nLeft: int):
        self._mineField.showMinesLeft(nLeft)

    def showGameover(self, win: bool):
        self._mulitplayerControls.showGameOver(win)

    def showMessage(self, msg: str):
        self._mulitplayerControls.showMessage(msg)
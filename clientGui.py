from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal
from multiplayerControlsGui import MultiplayerControlsGui

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


class ClientGui(MultiplayerControlsGui):
    join = pyqtSignal(str, int, str)
    leave = pyqtSignal()
    changeName = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ClientGui, self).__init__(parent)
        self._cltCtrl.changeName.connect(self._onChangeName)
        self._cltCtrl.connect.connect(self._onJoin)

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
        self._clearPlayerList()

    def connect(self):
        self._cltCtrl.btnJoin.setEnabled(True)
        self._cltCtrl.btnChgName.setEnabled(True)
        self._cltCtrl.btnJoin.setText("Leave")
        self._cltCtrl.txt_serverIp.setEnabled(False)
        self._cltCtrl.txt_serverPort.setEnabled(False)

    def _onChangeName(self):
        self.changeName.emit(self._cltCtrl.txtName.text())

    def _onJoin(self):
        if (self._cltCtrl.btnJoin.text() == "Join"):
            try:
                ip = self._cltCtrl.txt_serverIp.text()
                port = int(self._cltCtrl.txt_serverPort.text())
                name = self._cltCtrl.txtName.text()

                self.join.emit(ip, port, name)
            except:
                pass
        else:
            self.leave.emit()


    def _createLayout(self):
        self._controlsLayout = QHBoxLayout()
        self._intermediateLayout = QVBoxLayout()

        super(ClientGui, self)._createLayout()

        # remove all the old layout
        for i in range(0, 3):
            i = self._guiLayout.takeAt(0)
            self._guiLayout.removeItem(i)

        # reassemble new
        self._guiLayout.addLayout(self._controlsLayout)
        self._guiLayout.addLayout(self._layout)
        self._controlsLayout.addLayout(self._intermediateLayout)
        self._intermediateLayout.addWidget(self._turnLabel)
        self._intermediateLayout.addWidget(self._tableView)
        self._cltCtrl = ClientControlWidget(self)
        self._controlsLayout.addWidget(self._cltCtrl)

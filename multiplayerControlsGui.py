from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QLabel, QTableView, QSizePolicy, QAbstractItemView, QHBoxLayout
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QObject
from PyQt5.QtMultimedia import QSound
from minefieldGui import MinefieldGui


class Player(QObject):
    ipChanged = pyqtSignal()
    nameChanged = pyqtSignal()
    scoreChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        self._ip = "<not connected>"
        self.id = 0
        self._name = "<no name>"
        self._score = 0

    def getIP(self):
        return self._ip

    def setIP(self, ip):
        self._ip = ip
        self.ipChanged.emit()

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name
        self.nameChanged.emit()

    def getScore(self):
        return self._score

    def setScore(self, score):
        self._score = score
        self.scoreChanged.emit()

    ip = property(getIP, setIP, None)
    name = property(getName, setName, None)
    score = property(getScore, setScore, None)


class PlayerList(QAbstractTableModel):
    def __init__(self, parent=None):
        super(PlayerList, self).__init__(parent)
        self.__players = []

    def clear(self):
        for p in self.__players:
            self.removePlayer(p)

    def _update(self):
        i = self.index(0, 0)
        j = self.index(2, len(self.__players)-1)
        self.dataChanged.emit(i, j)

    def addPlayer(self, player):
        self.__players.append(player)
        player.nameChanged.connect(self._update)
        player.ipChanged.connect(self._update)
        player.scoreChanged.connect(self._update)
        l = len(self.__players)
        self.rowsInserted.emit(QModelIndex(), l, l)

    def removePlayer(self, player):
        self.__players.remove(player)
        l = len(self.__players)
        self.rowsRemoved.emit(QModelIndex(), l, l)

    def getPlayerById(self, id):
        for p in self.__players:
            if p.id == id:
                return p
        return None

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__players)

    def columnCount(self, parent: QModelIndex) -> int:
        return 3

    def data(self, index: QModelIndex, role):
        if (role == Qt.DisplayRole):
            col = index.column()
            row = index.row()
            if (col == 0):
                return self.__players[row].ip
            elif (col == 1):
                return self.__players[row].name + " (" + str(self.__players[row].id) + ")"
            elif (col == 2):
                return str(self.__players[row].score)
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


class MultiplayerControlsGui(MinefieldGui):
    def __init__(self, parent=None):
        self._mainLayout = None
        super(MultiplayerControlsGui, self).__init__(parent)

    # Override the layout method to not make the grid layout
    # the central layout of the widget
    def _createLayout(self):
        super(MultiplayerControlsGui, self)._createLayout()

        # This list holds all the current players
        self.__playerListModel = PlayerList(self)

        self._mpLayout = QVBoxLayout()
        self._turnLabel = QLabel(self)
        self._mpLayout.addWidget(self._turnLabel)

        self._tableView = QTableView()
        self._tableView.setMinimumSize(100, 100)
        self._tableView.verticalHeader().setVisible(False)
        self._tableView.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self._tableView.horizontalHeader().setVisible(False)
        self._tableView.setModel(self.__playerListModel)
        self._tableView.setColumnWidth(1, 100)
        self._tableView.setColumnHidden(0, True)
        self._tableView.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: None;")
        self._tableView.setShowGrid(False)
        self._tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self._mpLayout.addWidget(self._tableView)

        self._mainLayout = QVBoxLayout()
        self._mainLayout.addLayout(self._mpLayout)
        self._mainLayout.addLayout(self._layout)

        self.setLayout(self._mainLayout)

    def setLayout(self, layout):
        if (self._mainLayout != None):
            super(MultiplayerControlsGui, self).setLayout(self._mainLayout)

    def _clearPlayerList(self):
        self.__playerListModel.clear()
        self._turnLabel.clear()

    def addPlayer(self, id: int, ip: str):
        p = Player()
        p.id = id
        p.ip = ip
        self.__playerListModel.addPlayer(p)

    def removePlayer(self, id: int):
        p = self.__playerListModel.getPlayerById(id)
        if (p != None):
            self.__playerListModel.removePlayer(p)

    def changePlayerName(self, id: int, name: str):
        p = self.__playerListModel.getPlayerById(id)
        if p is not None:
            p.name = name

    def changePlayerScore(self, id: int, score: int):
        p = self.__playerListModel.getPlayerById(id)
        if p is not None:
            p.score = score

    def playersTurn(self, id: int, name: str):
        p = self.__playerListModel.getPlayerById(id)
        if p is not None:
            self._turnLabel.setText(p.name + "'s turn!")

    def yourTurn(self):
        self._turnLabel.setText("Your turn!")

    def showGameOver(self, win):
        if win:
            self._turnLabel.setText("GAME OVER! YOU WIN!")
        else:
            self._turnLabel.setText("GAME OVER! YOU LOSE!")
            s = QSound("assets/lose.wav")
            s.play()

    def showMessage(self, msg):
        self._turnLabel.setText(msg)

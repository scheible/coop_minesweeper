from PyQt5.QtWidgets import QMainWindow
from clientGui import ClientGui
from clientLogic import GameClient
from minefieldGui2 import MinefieldGui2
from minefieldGui import MinefieldGui


class TestWindow(QMainWindow):
    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle("TEST Minesweeper")
        self.setGeometry(50, 50, 500, 500)

        gui = MinefieldGui2(self)
        gui.reset(10, 10)
        self.setCentralWidget(gui)

        gui.uncovered.connect(self.uncover)
        gui.flagged.connect(self.flag)

    def uncover(self, x, y):
        print("uncover:", x, y)

    def flag(self, x, y):
        print("flagged:", x, y)
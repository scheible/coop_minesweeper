import sys
import unittest
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt
from clientGui import ClientGui
from PyQt5.QtWidgets import QApplication

class TestMultiplayerControlsGui(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)

    def test_gui(self):
        gui = ClientGui()
        gui.reset(10, 10)
        gui.addPlayer(1, "10.0.0.1")
        gui.changePlayerName(1, "Patrik")
        gui.changePlayerScore(1, 20)
        gui.yourTurn()
        gui.show()

        self.app.exec_()


if __name__ == '__main__':
    unittest.main()
import sys
import unittest
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt
from multiplayerControlsGui import MultiplayerControlsGui
from PyQt5.QtWidgets import QApplication

class TestMultiplayerControlsGui(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)

    def test_gui(self):
        gui = MultiplayerControlsGui()
        gui.addPlayer(0, "10.10.10.10")
        gui.addPlayer(1, "10.10.10.11")
        gui.changePlayerName(0, "Patrik")
        gui.changePlayerName(3, "Patrik")
        gui.yourTurn()
        gui.playersTurn(3, "")
        gui.show()

        self.app.exec_()


if __name__ == '__main__':
    unittest.main()
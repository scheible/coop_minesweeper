import sys
import unittest
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt
from minefieldGui import MineButton
from PyQt5.QtWidgets import QApplication

class TestMinefieldGui(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)

    def test_mineButton(self):
        button = MineButton(0, 0)
        button.show()
        spy = QSignalSpy(button.uncovered)
        spy2 = QSignalSpy(button.flagged)

        QTest.mouseClick(button, Qt.LeftButton)
        QTest.mouseClick(button, Qt.RightButton)

        self.assertEqual(len(spy), 1)
        self.assertEqual(len(spy2), 1)

        button.number(1)


    def test_numbers(self):
        button = MineButton(0, 0)
        button.show()
        button.number(1)

if __name__ == '__main__':
    unittest.main()
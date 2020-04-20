# coop_minesweeper
A multiplayer coop version of the well known minesweeper game. Made with Python and PyQt5.

# IDE
I used pyCharm to develop the project. However it is just a bunch of python files, so I think it is easy to manage

# PyQt
You need to install PyQt5 (preferably in an virtual environment) in order to execute the project.

On Windows:
1. Clone the project
2. Install python 3 by downloading the setup file from the python webstie. It also installs pip
2.5 Add python to your PATH variable
3. Install PyQt5 by running: python -m pip install pyqt
4. Install pyInstaller by running: python -m pip pyinstaller
4.5 Add the python/scripts directory to PATH
5. Create a standalone exectuable:
    pyinstaller -w main.py
    pyinstaller -w main_server.py

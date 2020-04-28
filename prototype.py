import random

def plotMineField(minefield, x_size, y_size):
    for y in range(0,y_size):
        for x in range(0,x_size):
            print(minefield[x][y],end=" ")
        print("")

def createEmptyField(minefield, x_size, y_size):
    for y in range(0, y_size):
        minefield.append([])

        for x in range(0,x_size):
            minefield[y].append(0)

def placeMines(minefield, nMines, x_size, y_size):
    minesPlaced = 0

    while (minesPlaced < nMines):
        x = random.randint(0,x_size-1)
        y = random.randint(0,y_size-1)

        if (minefield[x][y] == 0):
            minefield[x][y] = 'X'
            minesPlaced += 1

def isValidField(x,y):
    if (x >= 0) and (x < x_size) and (y >= 0) and (y < y_size):
        return True
    else:
        return False

def findNeighbourMines(minefield, x_center, y_center):
    n = 0
    for x in range(x_center-1, x_center+2):
        for y in range(y_center-1, y_center+2):
            if isValidField(x,y):
                if (minefield[x][y] == 'X'):
                    n += 1
    return n

def initMinefield(minefield, x_size, y_size):
    for y in range(0,y_size):
        for x in range(0,x_size):
            if (minefield[x][y] != 'X'):
                n = findNeighbourMines(minefield, x, y)
                minefield[x][y] = n



minefield = []
x_size = 10;
y_size = 10;
nMines = 20;

createEmptyField(minefield, x_size, y_size)
placeMines(minefield, nMines, x_size, y_size)
initMinefield(minefield, x_size, y_size)

plotMineField(minefield, x_size, y_size)
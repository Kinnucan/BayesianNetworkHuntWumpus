
import random


class WumpGrid(object):
    """A class to represent the wumpus wumpMap, used both by the environment and the hero agent."""


    def __init__(self, numRows, numCols):
        """Creates a blank world with the right rows and columns."""
        self.width = numCols
        self.height = numRows
        self.grid = dict()
        for r in range(numRows):
            for c in range(numCols):
                self.grid[r, c] = []


    def makeValidPos(self, row, col):
        """Takes in a row and column value and converts them to valid. If they are greater than the height
        or width then they are wrapped around, and similarly if they are negative they are wrapped around to the
        top end of the range."""
        row = row % self.height
        col = col % self.width
        return row, col

    def addHero(self, row, col):
        """Add the hero to the grid, and mark the square their in as 'seen'."""
        self.addInfo(row, col, 'hero')
        self.addInfo(row, col, 'SEEN')


    def addInfo(self, row, col, info):
        """Add the given info to the entry for the given row and column."""
        (row, col) = self.makeValidPos(row, col)
        if info not in self.grid[row, col]:
            self.grid[row, col].append(info)


    def getInfo(self, row, col):
        """Returns the list of information associated with a given cell, specified by row and columnm indices."""
        row, col = self.makeValidPos(row, col)
        data = self.grid[row, col]
        return data[:]


    def delInfo(self, row, col, info):
        """Given row and column indices, and a piece of data associated with that position, removes it from
        the list."""
        row, col = self.makeValidPos(row, col)
        self.grid[row, col].remove(info)


    def getSize(self):
        """Returns a tuple of the number of rows and number of columns in the grid."""
        return self.height, self.width

    def isFree(self, row, col):
        """Given row and column indices into the grid, returns True if the cell is free of any objects. Returns
        True if it is free and False otherwise."""
        (row, col) = self.makeValidPos(row, col)
        values = self.grid[row, col]
        for keyObst in ['wumpus', 'hero', 'bat', 'pit']:
            if keyObst in values:
                return False
        return True

    def findRandomFreeLoc(self):
        """Generates a new location that has no value in it."""
        while True:
            (randR, randC) = self.findRandomLoc()
            if self.isFree(randR, randC):
                break
        return randR, randC


    def findRandomLoc(self):
        """Generates a new random location, no constraints on what is already there."""
        randR = random.randrange(self.height)
        randC = random.randrange(self.width)
        return randR, randC


    def updateHeroPos(self, oldRow, oldCol, newRow, newCol):
        """Actually change the underlying map to put hero in new location."""
        self.delInfo(oldRow, oldCol, 'hero')
        self.addInfo(newRow, newCol, 'hero')
        self.addInfo(newRow, newCol, "SEEN")

    def updateBatPos(self, oldRow, oldCol, newRow, newCol):
        """Move a bat from one location to another."""
        self.delInfo(oldRow, oldCol, 'bat')
        self.addInfo(newRow, newCol, 'bat')


    def printGrid(self):
        """Print the entire contents of the map including pits, wumpus, hero, bats, slime, and blood."""
        print("    ", end="")
        for col in range(self.width):
            print(str(col).center(8), end="")
        print()
        for row in range(self.height):
            print("    " + "-" * 8 * self.width + "-")
            rowA = str(row).rjust(4)
            rowB = "    "
            for col in range(self.width):
                vals = self.grid[row, col]
                if 'SEEN' in vals:
                    filler = '.'
                else:
                    filler = ' '
                cellA = "|" + filler
                cellB = "|" + filler
                if 'wumpus' in vals:
                    cellA += 'Wu' + filler
                if 'pit' in vals:
                    cellA += 'Pi' + filler
                if 'hero' in vals:
                    cellA += "He" + filler
                if 'bat' in vals:
                    cellA += "Ba" + filler
                if 'blood' in vals:
                    cellB += "bl" + filler
                if 'slime' in vals:
                    cellB += "sl" + filler
                cellA = cellA.ljust(8, filler)
                cellB = cellB.ljust(8, filler)
                rowA += cellA
                rowB += cellB
            rowA += "|"
            rowB += "|"
            print(rowA)
            print(rowB)
        print("    " + "-" * 8 * self.width + "-")



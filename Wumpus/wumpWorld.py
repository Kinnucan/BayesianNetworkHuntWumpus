

import random
from wumpGrid import WumpGrid


class WumpWorld(object):
    """Represents a 2D wumpMap Wumpus world. In this world there is a wumpus, and pits, and bats. The
    bats are visible when you are in a room, the pits cause green slime on the adjacent walls, and the wumpus
    causes bloodstains in cells two steps away."""

    BAT_PROB = 0.3

    def __init__(self, rows, cols):
        """Creates the wumpMap and places the wumpus, the hero, the bats, and pits."""

        self.wumpMap = WumpGrid(rows, cols)
        self.heroRow = None
        self.heroCol = None
        self.heroAlive = True
        self.wumpusAlive = True
        self.unvisitedBats = []

        numCells = rows * cols
        batProb = 1/30
        pitProb = 1/24
        self.addObjects('wumpus', 1)
        self.addObjects('hero', 1)
        self.addRandomObjects('pit', pitProb)
        self.addRandomObjects('bat', batProb)


    def addObjects(self, objectType, numObj):
        """Adds numObj of the objectType objects to the wumpMap."""
        for i in range(numObj):
            row, col = self.wumpMap.findRandomFreeLoc()
            if objectType == 'hero':
                self.heroRow = row
                self.heroCol = col
                self.wumpMap.addHero(row, col)
            else:
                self.wumpMap.addInfo(row, col, objectType)
                if objectType == 'wumpus':
                    self.markWumpus(row, col)


    def addRandomObjects(self, objectType, objProb):
        """Given a type of object and the probability that each square will contain that object,
        consider each cell and determine whether or not to place that object at that square"""
        (rows, cols) = self.wumpMap.getSize()
        for r in range(rows):
            for c in range(cols):
                if self.wumpMap.isFree(r, c):
                    randProb = random.random()
                    if randProb < objProb:
                        self.wumpMap.addInfo(r, c, objectType)
                        if objectType == 'pit':
                            self.markPit(r, c)
                        elif objectType == 'bat':
                            self.unvisitedBats.append((r, c))

    def markPit(self, row, col):
        """Given the row and column of the pit, mark adjacent cells with slime."""
        for (r, c) in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
            self.wumpMap.addInfo(r, c, 'slime')

    def markWumpus(self, row, col):
        """Given the row and column of the wumpus, mark adjacenct cells with blood."""
        neighbors = [(row - 2, col), (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
                     (row, col - 2), (row, col - 1), (row, col + 1), (row, col + 2),
                     (row + 1, col - 1), (row + 1, col), (row + 1, col + 1), (row + 2, col)]
        for (r, c) in neighbors:
            self.wumpMap.addInfo(r, c, 'blood')

    def printWorld(self):
        """Print the grid and any other relevant information"""
        self.wumpMap.printGrid()


    def getHeroLoc(self):
        """Return the heros location as a tuple"""
        return self.heroRow, self.heroCol

    def isHeroAlive(self):
        """Returns True if the hero is still alive"""
        return self.heroAlive

    def isWumpusAlive(self):
        """Returns True if the wumpus is still alive"""
        return self.wumpusAlive

    def heroSenses(self):
        """Returns the information the hero would sense at the hero's location."""
        mapValues = self.wumpMap.getInfo(self.heroRow, self.heroCol)
        if 'hero' not in mapValues:
            print("heroSenses: hero location inconsistent with map!", self.heroRow, self.heroCol)
            return []
        mapValues.remove('hero')
        return mapValues

    def moveHero(self, direction):
        """Updates the map and the heros location by having it move in the given direction. At the edges, moving
        toward an edge does nothing. This must check if the hero has fallen into a pit or encountered the wumpus
        (and died), so it will return the new location if the hero has moved without dying, or the cause
         of death if the hero died."""
        newR, newC = self._nextLoc(self.heroRow, self.heroCol, direction)
        hasEnded = self.makeMove(newR, newC)
        if hasEnded:
            return hasEnded, (newR, newC)
        data = self.wumpMap.getInfo(newR, newC)
        if 'bat' in data:
            if (newR, newC) not in self.unvisitedBats:    # First visit to bat it never bugs you...
                batMoves = random.random()
                if batMoves > self.BAT_PROB:
                    print("Bat moving hero...")
                    batR, batC = self.wumpMap.findRandomLoc()
                    self.wumpMap.updateBatPos(newR, newC, batR, batC)
                    hasEnded = self.makeMove(batR, batC)
                    if hasEnded:
                        return hasEnded, (batR, batC)
                    return 'bat', (newR, newC, batR, batC)
            else:
                self.unvisitedBats.remove((newR, newC))
        return 'move', (newR, newC)


    def makeMove(self, newR, newC):
        """Given a new location, this updates the map and then checks for end of game, returns the result for
        checking for game end."""
        self.wumpMap.updateHeroPos(self.heroRow, self.heroCol, newR, newC)
        self.heroRow = newR
        self.heroCol = newC
        return self.checkEndOfGame(newR, newC)


    def checkEndOfGame(self, row, col):
        """Check if the hero moving to the given row and column causes the hero to die, losing the game
        to a wumpus or pit."""
        data = self.wumpMap.getInfo(row, col)
        if 'wumpus' in data:
            self.heroAlive = False
            return 'wumpus'
        elif 'pit' in data:
            self.heroAlive = False
            return 'pit'
        else:
            return False



    def shootArrow(self, direction):
        """Given the direction relative to hero's position, this fires the hero's arrow in that direction. If the
        wumpus is in the room where the arrow goes, then the wumpus is killed and the hero wins the game. Otherwise
        the hero dies (because the wumpus comes to their location and eats them."""
        arrowR, arrowC = self._nextLoc(self.heroRow, self.heroCol, direction)
        data = self.wumpMap.getInfo(arrowR, arrowC)
        if 'wumpus' in data:
            self.wumpusAlive = False
            return True
        else:
            self.heroAlive = False
            return 'wumpus'

    def _nextLoc(self, row, col, direct):
        """Given the direction to move in, this computes the next location in that direction. No wrapping around,
        this will produce indices outside the bounds of the grid."""
        if direct == 'north':
            return self.wumpMap.makeValidPos(row - 1, col)
        elif direct == 'south':
            return self.wumpMap.makeValidPos(row + 1, col)
        elif direct == 'east':
            return self.wumpMap.makeValidPos(row, col + 1)
        elif direct == 'west':
            return self.wumpMap.makeValidPos(row, col - 1)
        else:
            print("WumpWorld.movehero: Invalid direction of movement:", direct)
            return self.wumpMap.makeValidPos(row, col)




if __name__ == "__main__":
    # wump1 = WumpWorld(6, 8)
    # wump1.printWorld()

    wump2 = WumpWorld(5, 5)
    while True:
        wump2.printWorld()
        senses = wump2.heroSenses()
        print("Senses:", senses)
        move = input("Input movement or quit: ")
        if move in ['q', 'quit']:
            break
        res = wump2.moveHero(move)
        print(res)




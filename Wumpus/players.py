
import random
from wumpGrid import WumpGrid



class Player(object):
    """Represents what the player knows, and has methods for getting player's choice of action
    from what the player knows."""

    def __init__(self, playerLoc, gridSize):
        """Given a tuple for the player's starting location, and a tuple for the size
        of the wumpMap, this sets up the player's initial knowledge."""
        self.heroRow, self.heroCol = playerLoc
        self.gridHeight, self.gridWidth = gridSize
        self.knowledge = WumpGrid(self.gridHeight, self.gridWidth)
        self.knowledge.addHero(self.heroRow, self.heroCol)


    def nextAction(self, currentSenses):
        """Decides on the next action, one of "go north", "go south", "go east", "go west", or
        shoot north, shoot south, shoot east, or shoot west."""
        self.updateKnowledge(currentSenses)
        actions = ["go north", "go south", "go east", "go west",
                   "shoot north", "shoot south", "shoot east", "shoot west"]
        return random.choice(actions)

    def updateKnowledge(self, sensorData):
        """Updates the knowledge base to incorporate any curent sensor information (blood or
        slime). Input is a list containing any sensor values that there are."""
        for sense in sensorData:
            self.knowledge.addInfo(self.heroRow, self.heroCol, sense)

    def playerMoved(self, result, newLoc):
        """Updates player's position in Player's map."""

        if result == 'bat':
            # Movement was due to a bat, move both bat and hero
            (wasBatR, wasBatC, newR, newC) = newLoc
            self.knowledge.updateBatPos(wasBatR, wasBatC, newR, newC)
            self.knowledge.updateHeroPos(self.heroRow, self.heroCol, newR, newC)
            self.heroRow = newR
            self.heroCol = newC
        elif result == 'move':
            newR, newC = newLoc
            self.knowledge.updateHeroPos(self.heroRow, self.heroCol, newR, newC)
            self.heroRow = newR
            self.heroCol = newC
        else:
            print("Player didn't move.")




class UserPlayer(Player):
    """Interacts with the user to get the next action."""

    def nextAction(self, currentSenses):
        """Prints the player's current data and information, and then asks the player for an action."""
        self.updateKnowledge(currentSenses)
        self.knowledge.printGrid()
        act = self.getUserAction()
        return self._codeToAct(act)

    def getUserAction(self):
        """Asks the user for input until they give valid input, then reports the action"""
        act = None
        while act not in ['mn', 'ms', 'me', 'mw', 'sn', 'ss', 'se', 'sw', 'q']:
            print('Actions:')
            print(" mn: Move north      sn: Shoot north")
            print(" ms: Move south      ss: Shoot south")
            print(" me: Move east       se: Shoot east")
            print(" mw: Move west       sw: Shoot west")
            print('  q: Quit')
            act = input("Enter your choice: ")
        return act


    def _codeToAct(self, code):
        """Converts one or two letter codes into tuples with full words."""
        if code == 'mn':
            return ('move', 'north')
        elif code == 'ms':
            return ('move', 'south')
        elif code == 'me':
            return ('move', 'east')
        elif code == 'mw':
            return ('move', 'west')
        elif code == 'sn':
            return ('shoot', 'north')
        elif code == 'ss':
            return ('shoot', 'south')
        elif code == 'se':
            return ('shoot', 'east')
        elif code == 'sw':
            return ('shoot', 'west')
        else:
            return code



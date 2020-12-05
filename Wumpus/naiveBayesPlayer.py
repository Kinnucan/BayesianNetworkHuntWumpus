

from naivebayes import NaiveBayes
from players import UserPlayer


class NaiveBayesPlayer(UserPlayer):
    """This uses a Naive Bayes network to determine how safe the squares for all squares adjacent to
    known squares. It picks the safest to go to, and then, plans a route to get to that square through
    only known, safe squares."""

    def __init__(self, playerLoc, gridSize):
        """Sets up a set of locations that have not been visited, but whose neighbor cells have been
        visited (kind of like the fringe in a state-space search). It also has a set of known cells."""
        UserPlayer.__init__(self, playerLoc, gridSize)
        self.known = {(self.heroRow, self.heroCol)}
        self.fringe = set()
        self._addNeighborsToFringe((self.heroRow, self.heroCol))
        self.pitNaiveNet = NaiveBayes(mode="file", networkFile="findPit8by8.txt")
        self.wumpusNaiveNet = NaiveBayes(mode="file", networkFile="WumpusAt_r,c")
        self.currentPath = [] # 'north', 'east', 'east', 'south']

        self.isPitLocProbs = []
        self.isWumpusLocProbs = []
        self.isDangerLocProbs = []


    def nextAction(self, currentSenses):
        """Updates the knowledge grid with new knowledge, and then it has two modes. In the first mode,
        it has already generated a path through known cells to get to a fringe cell, and it just needs to
        carry it out. In the second mode, it needs to choose a new fringe cell to move to. It calls the
        Naive Bayes network on each fringe cell, storing the probability it is safe in a dictionary.
        Finally, it chooses the "safest" option and plans a route to that cell, storing it in currentPath
        and taking the first step toward it."""
        self.updateKnowledge(currentSenses)
        self.knowledge.printGrid()

        print("Current path =", self.currentPath)

        if self.currentPath != []:
            print("...Continuing current planned path")
            nextStep = self.currentPath[0]
            self.currentPath.pop(0)
            nextAction = 'move'
            nextDir = nextStep
        else:
            # For each fringe location, use the naive Bayes network to compute how likely it is to contain a pit or a wumpus
            print("...Choosing most safe neighbor cell")
            self.isPitLocProbs = []
            self.isWumpusLocProbs = []
            self.isDangerLocProbs = [] # "danger" means "has either pit or wumpus" -- i.e., "has at least one thing that kills you"
            for loc in self.fringe:
                influences = self._getInfluences(loc)
                self.pitNaiveNet.resetNetwork()
                self.wumpusNaiveNet.resetNetwork()
                for infl in influences:
                    info = influences[infl]
                    # First handle slime
                    attribute = self._makeAttributeName(infl, 'slimeAt')
                    if sum([abs(x) for x in infl]) == 1: # Slime only cares about cells 1 away from original
                        if 'slime' in info:
                            self.pitNaiveNet.setFeature(attribute, 'yes')
                        else:
                            self.pitNaiveNet.setFeature(attribute, 'no')
                    # Then handle blood
                    attribute = self._makeAttributeName(infl, 'bloodAt')
                    if 0 < sum([abs(x) for x in infl]) <= 2:  # Blood cares about cells up to 2 away from original
                        if 'blood' in info:
                            self.wumpusNaiveNet.setFeature(attribute, 'yes')
                        else:
                            self.wumpusNaiveNet.setFeature(attribute, 'no')

                pitProb = self.pitNaiveNet.getNormedOutputProb('yes')
                wumpusProb = self.wumpusNaiveNet.getNormedOutputProb('yes')
                dangerProb = pitProb + wumpusProb - (pitProb * wumpusProb)
                self.isPitLocProbs.append((loc, pitProb))
                self.isWumpusLocProbs.append((loc, wumpusProb))
                self.isDangerLocProbs.append((loc, dangerProb))

            # Now, sort the locations based on their probabilities, lowest first
            self.isDangerLocProbs.sort(key=lambda tup: tup[1])  # sort by probability

            for (chosenLoc, chosenProb) in self.isDangerLocProbs:
                # Try generating paths to cells from best to worst until one is reachable
                print("Trying to plan to cell at", chosenLoc, "with isDanger probability of", chosenProb)
                # Plan a path from current loc to chosen loc
                isPathCreated = self.planPath(chosenLoc)
                if isPathCreated:
                    break

            print("self.currentPath", self.currentPath)
            nextStep = self.currentPath[0]
            self.currentPath.pop(0)
            nextAction = 'move'
            nextDir = nextStep

        # If a wumpus is likely in a neighboring cell, ignore all other plans and shoot it
        wumpusProbDict = dict(self.isWumpusLocProbs)
        for (dr, dc, dir) in [(-1, 0, 'north'), (1, 0, 'south'), (0, -1, 'west'), (0, 1, 'east')]:
            neighborToCheck = self.knowledge.makeValidPos(self.heroRow + dr, self.heroCol + dc)
            prob = wumpusProbDict.get(neighborToCheck)
            if prob != None:
                if prob >= .95:
                    print("Strong probability (" + str(prob) + ") of wumpus due " + dir)
                    nextAction = "shoot"
                    nextDir = dir

        # Now, let user override if they want
        print("Chosen action is:", nextAction, nextDir)
        resp = input("Hit enter/return if you concur or 'n' to input your own action: ")
        if resp == 'n':
            # If user overrides player, then player should start over at next step
            self.currentPath = []
            act = self.getUserAction()
            return self._codeToAct(act)
        else:
            return nextAction, nextDir



    def _makeAttributeName(self, offset, infoType):
        """Given a tuple with x and y offsets and the name of the information type (slimeAt, bloodAt)
        this returns the proper attribute name for slime at thatlocation."""
        rowOff, colOff = offset
        rowStr = self._offsetToString(rowOff)
        colStr = self._offsetToString(colOff)
        return infoType + "_r" + rowStr + "_c" + colStr


    def _offsetToString(self, offset):
        """Given an offset, an integer in the range from -2 to 2, this returns a string version.
        It gives the empty string if the offset is 0, and otherwise converts the int to a str,
        adding a plus sign for positive values."""
        if offset == 0:
            return ""
        elif offset < 0:
            return str(offset)
        else:
            return '+' + str(offset)

    def planPath(self, newLoc):
        """Given a new location, plan a route for the hero from their current location to the new location,
        passing through only known cells. Returns True if the search generated a path, and False otherwise.
        NOTE: if a bat moves the hero to a new location, it may not be possible to access some fringe locations, thus
        this search may fail."""
        newRow, newCol = newLoc
        queue = [[self.heroRow, self.heroCol, []]]
        visited = {(self.heroRow, self.heroCol)}
        while queue != []:
            currR, currC, currPath = queue[0]
            queue.pop(0)
            for (dr, dc, dir) in [(-1, 0, 'north'), (1, 0, 'south'), (0, -1, 'west'), (0, 1, 'east')]:
                nextLoc = self.knowledge.makeValidPos(currR + dr, currC + dc)
                if nextLoc not in visited:
                    newPath = currPath + [dir]
                    if newLoc == nextLoc:
                        self.currentPath = newPath
                        return True
                    if nextLoc in self.known:
                        queue.append([nextLoc[0], nextLoc[1], newPath])
                    visited.add(nextLoc)
        print("Path planning to", newLoc, "failed, no path available through known squares")
        return False

    def playerMoved(self, result, newLoc):
        """Overriding parent methed so that we can update the fringe and known sets."""
        UserPlayer.playerMoved(self, result, newLoc)
        oldLoc = self.heroRow, self.heroCol
        if len(newLoc) > 2:
            # player was moved by a bat, erase any path that was planned and start over
            self.currentPath = []
            newLoc = newLoc[2:]
        if newLoc in self.fringe:
            self.fringe.remove(newLoc)
        self.known.add(newLoc)
        self._addNeighborsToFringe(newLoc)


    def _addNeighborsToFringe(self, loc):
        """Given a location tuple, add its neighbors to the fringe set if they are not already known
        or in fringe already."""
        locRow, locCol = loc
        for (dr, dc) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nextLoc = self.knowledge.makeValidPos(locRow + dr, locCol + dc)
            if nextLoc not in self.known and nextLoc not in self.fringe:
                self.fringe.add(nextLoc)

    def _getInfluences(self, loc):
        """Given a location, determine which of the 12 states within 2 of it are known. Returns
         a dictionary where the key is the offset from the current location, and the value is what is known
         about that location."""
        influences = {}
        (r, c) = loc
        for (dr, dc) in [(-2, 0), (-1, 1), (-1, -1), (-1, 0),
                         (1, 0), (1, 1), (1, -1), (2, 0),
                         (0, -2), (0, -1), (0, 1), (0, 2)]:
            nextLoc = self.knowledge.makeValidPos(r + dr, c + dc)
            if nextLoc in self.known:
                whatsThere = self.knowledge.getInfo(nextLoc[0], nextLoc[1])
                influences[dr,dc] = whatsThere
        return influences



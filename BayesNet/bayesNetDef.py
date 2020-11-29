
import random


class BayesNet:
    """Enables the construction of a Bayesian network. Initially empty, there
    are methods for adding nodes, edges, and filling in the conditional
    probability tables for the bayes net. Additional methods report
    probabilities"""

    # ======================================================================
    # This first section of methods are used to build the bayesian network


    def __init__(self):
        """Initializes the network to be empty"""
        self.nodeOrder = []
        self.nodeList = []
        self.nodeValues = {}
        self.edges = {}
        self.revEdges = {}
        self.cpts = {}
        self.currentKnowns = {}

    
    def addNode(self, nodeName, nodeValues):
        """Given a string node name and a list of node values (typically
        strings) this adds the node to the Bayesian Network, with no edges"""
        self.nodeValues[nodeName] = nodeValues
        self.nodeList.append(nodeName)
        self.edges[nodeName] = []
        self.revEdges[nodeName] = []

    def editNode(self, nodeName, nodeValues):
        """Given a string node name and a list of node values (typically
        strings) this updates the node...if the node does not exist, then
        this adds it"""
        if nodeName in self.nodeValues:
            self.nodeValues[nodeName] = nodeValues
        else:
            self.addNode(nodeName, nodeValues)
            
    def deleteNode(self, nodeName):
        """Given a string node name, it removes the node from the graph,
        including any edges that involved the node"""
        if nodeName in self.nodeValues:
            del self.nodeValues[nodeName]
            self.nodeList.remove(nodeName)
            forEdges = self.edges[nodeName]
            backEdges = self.revEdges[nodeName]
            del self.edges[nodeName]
            del self.revEdges[nodeName]
            for neighbor in forEdges:
                neighEdges = self.revEdges[neighbor]
                neighEdges.remove(nodeName)
            for neighbor in backEdges:
                neighEdges = self.edges[neighbor]
                neighEdges.remove(nodeName)
            
        
        
    def addEdge(self, node1, node2):
        """Given two node names, it adds an edge in between them. Since we
        also want to be able to get the parents of a node, we keep a list of
        "reverse-order" edges as well"""
        if node1 not in self.nodeValues:
            print("Node does not exist:", node1)
        elif node2 not in self.nodeValues:
            print("Node does not exist:", node2)
        else:
            self.edges[node1].append(node2)
            self.revEdges[node2].append(node1)

    def deleteEdge(self, node1, node2):
        """Given two nodes, remove the edge(s) between them"""
        if (node1  in self.nodeValues) and (node2 in self.nodeValues):
            if node1 in self.revEdges[node2]:
                self.edges[node1].remove(node2)
                self.revEdges[node2].remove(node1)
                
                
                
    def getNodeNames(self):
        """Return a list of the nodes in the Bayesian Network"""
        return self.nodeList[:]
    
    
    def getNodeValues(self, nodeName):
        """For a given node, return a list containing the node values"""
        if nodeName in self.nodeValues:
            return self.nodeValues[nodeName][:]
        else:
            return []

    def getNeighbors(self, nodeName):
        """For a given node, return a list of the nodes it has an edge TO"""
        if nodeName in self.edges:
            return self.edges[nodeName][:]
        else:
            return []
    
    
    def getPredecessors(self, nodeName):
        """For a given node, return a list of the nodes that have edges to this one"""
        if nodeName in self.revEdges:
            return self.revEdges[nodeName][:]
        else:
            return []
    
    def setupCPTables(self):
        """Given the structure of the network, create a set of Conditional Probability
        tables."""
        if self.cpts == {}:
            for nodeName in self.nodeOrder:
                self.cpts[nodeName] = {}
                allGivens = self.buildGivens(nodeName)
                for value in self.nodeValues[nodeName]:
                    self.cpts[nodeName][value] = {}
                    for given in allGivens:
                        self.cpts[nodeName][value][tuple(given)] = 0.0
        
        
    def addCPTableValue(self, nodeName, nodeValue, givens, probValue):
        if type(givens) != tuple:
            givens = tuple(givens)
        self.cpts[nodeName][nodeValue][givens] = probValue
    
    
        
    # ======================================================================
    # --------------------------
    # Next section includes ways to fill out the bayes net
    
    def backdoorFill(self, oldCPT):
        """This is a hack to allow me to specify the CP tables directly,
        rather than doing so interactively"""
        if self.nodeOrder == []:
            self.setOrdering()
        self.cpts = oldCPT
            
    def readBayesNet(self, filename):
        """Takes in a filename and reads a description of a Bayesian Network
        from the file, building the corresponding object."""
        fileObj = open(filename, 'r')
        
        readMode = None
        for line in fileObj:
            line = line.strip()
            lowerLine = line.lower()
            lineParts = line.split()
            if line.isspace():
                continue
            elif line == "---":
                readMode = None
            elif readMode is None and lowerLine == "nodes":
                readMode = "Nodes"
            elif readMode == "Nodes":
                nodeName = lineParts[0]
                nodeValues = lineParts[1:]
                self.addNode(nodeName, nodeValues)
                print("Node", nodeName, nodeValues)
            elif readMode is None and lowerLine == 'edges':
                readMode = "Edges"
            elif readMode == "Edges":
                fromNode = lineParts[0]
                toNode = lineParts[1]
                self.addEdge(fromNode, toNode)
                print("Edge", fromNode, toNode)
            elif readMode is None and lowerLine == 'tables':
                self.setOrdering()
                self.setupCPTables()
            elif readMode is None and 'cpt' in lowerLine:
                cptNode = lineParts[1]
                readMode = "CPT"
            elif readMode == "CPT":
                if line.count(']') != 1:
                    print("Line has more than one ]: uh-oh!")
                split1 = line.split(']')
                givenStr = split1[0][1:]
                probStr = split1[1]
                givenBinds = self.equalsToDict(givenStr)
                print("GivenBinds", givenBinds)
                givenOrder = self.getPredecessors(cptNode)
                givenList = []
                for g in givenOrder:
                    bind = givenBinds[g]
                    givenList.append(bind)
                probs = self.equalsToDict(probStr)
                for val in probs:
                    prob = float(probs[val])
                    #print("Adding...", cptNode, val, givenList, prob)
                    self.addCPTableValue(cptNode, val, givenList, prob)
        fileObj.close()
                
                
    def equalsToDict(self, strOfEqs):
        """Given a string of the form "x1 = y1 x2 = y2 ..." break it up and 
        build a dictionary with x's as keys and y's as values."""
        eqList = strOfEqs.split()
        i = 0
        ans = {}
        while i < len(eqList):
            if eqList[i+1] != '=':
                print("Uh-oh, something got off")
            lhs = eqList[i]
            rhs = eqList[i+2]
            ans[lhs] = rhs
            i = i + 3
        return ans
    


    def fillCPTables(self):
        """Interactively asks the user to enter probabilities for each slot in
        the conditional probability tables.  All nodes and edges must be added to the
        network before this function is called!"""
        if self.nodeOrder == []:
            self.setOrdering()
        self.cpts = {}
        for node in self.nodeOrder:
            print("=======================================")
            print("Entering probabilities for the CPT for node", node)

            self.cpts[node] = {}
            inNodes = self.revEdges[node]
            allGivens = self.recGivensBuild(inNodes, 0)
            for givens in allGivens:
                numVals = len(self.nodeValues[node])
                cnt = 0
                totProb = 0
                for value in self.nodeValues[node]:
                    if value not in self.cpts[node]:
                        self.cpts[node][value] = {}
                    print("Consider the probability of", node, 'having value', value, "given:")
                    if givens == []:
                        print("   No conditions")
                    else:
                        for n, g in zip(inNodes, givens):
                            print(" ", n, "is", g)
                    if cnt < numVals - 1:
                        probStr = input("Enter the probability: ")
                        probVal = float(probStr)
                        totProb += probVal
                    else:
                        probVal = 1.0 - totProb
                        print("All other probabilities known, this one must be:", probVal)
                    self.cpts[node][value][tuple(givens)] = probVal
                    print("Adding table value:", node, value, givens, self.cpts[node][value][tuple(givens)])
                    cnt += 1
                print()



    def buildGivens(self, nodeName):
        """Given the name of a node, it builds a list of lists that contains all the possible combinations of values from incoming edges"""
        if nodeName in self.nodeValues:
            return self.recGivensBuild(self.revEdges[nodeName], 0)
        
        
    def recGivensBuild(self, inEdges, pos):
        """Given a set of edges coming into some node, and a position into
        that list of edges, this makes a list of sublists, where each sublist
        contains some combination of the values of the parent nodes. The list
        of sublists contains *ALL* combinations of parent node values. Each
        combination corresponds to a row in the CPT for the node in
        question"""
        if pos == len(inEdges):
            return [[]]
        elif pos == len(inEdges) - 1:
            return [[val] for val in self.nodeValues[inEdges[pos]]]
        else:
            recLists = self.recGivensBuild(inEdges, pos+1)
            opts = []
            for val in self.nodeValues[inEdges[pos]]:
                opts.extend([[val] + d[:]for d in recLists])
            return opts


    def setOrdering(self):
        """This function takes the set of nodes, and orders them in
        topological order, so that nodes with no parents come first, and then
        nodes that depend only on previously added nodes"""
        self.nodeOrder = []
        nodesNotIn = self.nodeList[:]
        while nodesNotIn != []:
            nextNode = nodesNotIn[0]
            nodesNotIn.pop(0)
            allGivensIn = True
            for hidden in self.revEdges[nextNode]:
                if hidden not in self.nodeOrder:
                    allGivensIn = False
                    break
            if allGivensIn:
                self.nodeOrder.append(nextNode)
            else:
                nodesNotIn.append(nextNode)



    # ======================================================================
    # The functions below take a completed network and compute conjunctive
    # or conditional probabilities for features of the network.  The askProbs
    # method allows the user to interactively specify what
    # probability/ies the user wants

    def addKnown(self, nodeName, nodeValue):
        """Given the name of a node and a value, it sets
        that node to have the given value"""
        if nodeName in self.nodeValues and nodeValue in self.nodeValues[nodeName]:
            self.currentKnowns[nodeName] = nodeValue
            
    def deleteKnown(self, nodeName):
        """Given the name of a node, it removes the entry in the knowns dictionary for that node"""
        if nodeName in self.currentKnowns:
            del self.currentKnowns[nodeName]
            
            
    def resetKnowns(self):
        """Removes all knowns"""
        self.currentKnowns = {}
        
        
    def askProbs(self):
        """Asks the user to select what kind of probability they want.  the result
        is printed and returned"""
        which = input("Do you want to compute (1) conditional or (2) conjunctive probabilities: ")
        if "1" in which:
            node = input("Enter the node for which to compute the probability distribution: ")
        else:
            node = None
        knowns = self.askKnowns(node)
        if "1" in which:
            pd = self.computeProbDist(node, knowns)
            self.printPD(pd)
            return pd
        else:
            prob = self.computeProbabilities(knowns)
            print(prob)
            return prob


    def askKnowns(self, node = None):
        """Given an optional node name, it asks the user to enter nodes whose
        values are known, checking that they don't try to enter node. It
        builds a dictionary whose keys are the nodes and whose values are the
        values"""
        nextNode = None
        knownDict = {}
        while nextNode != "exit":
            nextNode = input("Enter the name of the next node whose value is known (or exit if done): ")
            if nextNode == "exit":
                break
            elif nextNode == node:
                print("You chose that node to compute a probability distribution, you cannot assign it a value now!")
            else:
                nextValue = input("Enter the value for node " + nextNode + ": ")
                knownDict[nextNode] = nextValue
        return knownDict


    # ----- NOTE: I changed the representation of the knowns, so that now it
    # ----- is not a list of lists, but a dictionary with the node names as
    # ----- the keys, and the values as the values

    def computeProbDist(self, node, knowns):
        """Given a node, this uses the set of known values for nodes stored
        in self.currentKnowns, where the keys are the nodes and the values
        are the values, this function computes the probability distribution
        _P_(node | knownDict). The probability distribution is represented as
        a dictionary, where the keys are the values node can take on, and the
        value is the conditional probability of that value"""
        probDist = {}
        for value in self.nodeValues[node]:
            newKnowns = knowns.copy()   #self.currentKnowns.copy()
            newKnowns[node] = value
            probDist[value] = self.computeProbabilities(newKnowns)
        self.normalize(probDist)
        return probDist

    
    def computeProbabilities(self, knownDict = None):
        """Given a dictionary of known values for nodes, this function
        computes the probability of that conjunction of factors taking place.
        The work is actually done by a recursive helper function If no
        dictionary is passed in, then this uses self.currentKnowns"""
        if knownDict is None:
            knownDict = self.currentKnowns.copy()
        return self.recComputProb(self.nodeOrder, 0, knownDict, 0)


    def recComputProb(self, nodes, pos, knownDict, indent = 0):
        """This takes a list of nodes, in a pre-determined topological sorted
        order a position in that list, and the dictionary of nodes and values
        we are assuming to be true, and it recursively computes the
        probability of those knowns. When it reaches a variable where the
        value is not known, it compute separate probabilities for each
        possible value of the variable, and then adds them up. The indent
        argument just allows this function to print out what it is doing in
        such a way that the recursion is clear: the deeper the recursion, the
        greater the indent"""
        if pos == len(nodes):
            return 1.0
        else:
            nextNode = nodes[pos]
            print("   " * indent, "Looking at node", nextNode)
            knownValue = self.findValue(nextNode, knownDict)
            if knownValue != None:
                print("   " * indent, "...Value known:", knownValue)
                print("   " * indent, knownDict)
                currProb = self.lookupCPT(nextNode, knownValue, knownDict)
                print("   " * indent, "  Multiplying by probability:", currProb)
                rest = self.recComputProb(nodes, pos+1, knownDict, indent+1)
                print("   " * indent, currProb, "has type", type(currProb), rest, "has type", type(rest))
                return currProb * rest
            else:
                print("   " * indent, "...Unknown, summing!=================")
                sumProb = 0
                for val in self.nodeValues[nextNode]:
                    print("   " * indent, nextNode, "...Next value =", val)
                    newKnowns = knownDict.copy()
                    #print("   " * indent, "  newKnowns =", newKnowns)
                    newKnowns[nextNode] = val
                    currProb = self.lookupCPT(nextNode, val, knownDict)
                    print("   " * indent, "  Multiplying by probability:", currProb)
                    rest = self.recComputProb(nodes, pos + 1, newKnowns, indent + 1)
                    sumProb += currProb * rest
                print("   " * indent, "=====================================")
                return sumProb


    def lookupCPT(self, node, value, knownDict):
        """Given a node, its value, and the dictionary of known variables and
        values, this function looks up the correct entry in the CPT"""
        #print("Look up:", node, value, knownDict)
        givens = []
        for parent in self.revEdges[node]:
            val = self.findValue(parent, knownDict)
            if val is None:
                print("UH-OH: a missing value!", parent, knownDict)
                return 0.0
            givens.append(val)
        #print("Givens =", tuple(givens))
        prob = self.cpts[node][value][tuple(givens)]
        return prob
        


    def findValue(self, nodeName, knowns):
        """Given a node name and the dictionary of knowns, it looks to see if
        there is an entry in the known list for that """
        #print("Find value of", nodeName, "in", knowns)
        if nodeName in knowns:
            return knowns[nodeName]
        else:
            return None


    def normalize(self, probDict):
        """Given a set of probabilities, re-scale them so that they add up to
        one (applying the alpha term to the distribution"""
        if len(probDict) == 0:
            print("ERROR: distribution can't be empty")
            return
        total = 0.0
        for value in probDict:
            total += probDict[value]

        if total == 0.0:
            print("ERROR: probabilities to be normalized cannot add to zero")
            return

        for value in probDict:
            probDict[value] = probDict[value] / total

    
    def printPD(self, probDict):
        formatStr = "P({0:s}) = {1:6.2f}"
        for key in probDict:
            print(formatStr.format(key, probDict[key]))
            #print("P(", key, ") =", probDict[key])


    # ======================================================================
    # This next section implements sampling algorithms for inexact inference


    # -----------------------------
    # MCMC, Gibbs Sampling
    
    def gibbsSampling(self, queryNode, evidenceDict, numSteps):
        """Performs Gibbs sampling on the network. Generates an initial random set of values, fixing the evidence
        values. Then it moves about in the state space of possible events, changing one non-evidence value at a time
        (including possibly staying in the same state). It changes the value based on a probability distribution of
        values for that node, given the Markov Blanket of the node (parents, children, and children's parents).
        It repeats this N times the number of non-evidence variables, counting the frequency of each possible query
        value in the process. Finally, it normalizes the counts to be probabilities that sum to 1.0, and returns it."""
        # Get samples by walk
        pass   #TODO: Define this method, in conjunction with the three methods below to implement the Gibbs sampling algorithm
        # Get samples by walk
        # Set up count of each queryNode outcome
        # Turn counts into probabilities

        
    def gibbsGetSamples(self, evidenceDict, numBigSteps):
        """Builds a list of samples generated in the Gibbs sampling way, for the given number of "big steps". Each sample
        is a dictionary where the key is the random variable and the value is the assigned value for that variable.
        Each big step iterates through a sequence of samples, one for each non-evidence node in the network. Returns a list
        of all samples visited in the walk."""
        pass  # TODO: Define this method, in conjunction with the other three methods to implement the Gibbs sampling algorithm


    def randomAssign(self, evidence):
        """Creates a new event by randomly assigning values to those nodes that don't have them fixed by the evidence.
        This random assignment is done without respect to probabilities. Returns the sample (a dictionary as described above)."""
        pass  # TODO: Define this method, in conjunction with the other three methods to implement the Gibbs sampling algorithm
    

    def markovBlanketProbs(self, node, currEvent):
        """Given a non-evidence node and the current assignment of nodes to values, compute the probability
        distribution P(Node | mb(Node)), which means for each value of the node, multiplying the probability
        of that value given the node's parent values, times the probability of each child value given the child's
        parents' values.
        Assumes that it need to change the current node's value in a copy of the current event for computing
        children's probabilities.
        Returns the computed probability distribution, a dictionary where the keys are values and the values are the probabilities, which
        must sum to 1.0"""
        pass  # TODO: Define this method, in conjunction with the other three methods to implement the Gibbs sampling algorithm


    # ----------------------------------------------------
    # Likelihood weighting
    
    def likelihoodWeighting(self, queryNode, evidenceDict, numSamples):
        """Takes in a query node, a dictionary of evidence, and the number
        of samples to compute, and it generates that many weighted samples,
        where the evidence is fixed, and it uses the weights to compute
        the probability distribution.  Returns the probability distribution (a dictionary with values of query variable
        for keys and probabilities for values."""
        pass  # TODO: Implement this using the algorithm from the reading, and the helper functions below
        # get samples
        # set up total weights for each value of query node
        # add sample's weight to appropriate query node value
        # convert to probability distribution


    def likelihoodWeightingSamples(self, evidenceDict, numSamples):
        """Build a list of samples paired with their weights, given a dictionary of evidence and the number
        of samples to build. Returns the list of tuples. Each tuple contains a sample (each sample is a dictionary with
        a random variable for the key and the assigned value) and its weight)."""
        pass  # TODO: Implement this helper using the algorithm from the reading

    
    def weightedSample(self, evidence):
        """Takes in a dictionary of evidence, and fills it out to be a full event by randomly selecting for those nodes
        not specified. It returns a tuple of the event/sample and a weight that is the product of the probabilities of
        the evidence nodes."""
        pass  # TODO: Implement this helper using the algorithm from the reading


    
    # -----------------------------
    # Rejection sampling
    
    def rejectionSampling(self, queryNode, evidenceDict, numSamples):
        """Takes in a query variable, a dictionary of known values, and the 
        number of samples to generate, and it estimates the probability
        distribution P(Q | e) using the samples."""
        samples = self.priorSampling(numSamples)
        matchingSamples = self.selectConsistent(samples, evidenceDict)
        if len(matchingSamples) == 0:
            print("No samples found, try again and increase number of samples")
            return None
        nodeValues = self.getNodeValues(queryNode)
        countValues = {}
        for val in nodeValues:
            countValues[val] = 0
        for inst in matchingSamples:
            instVal = inst[queryNode]
            countValues[instVal] += 1
        probs = {}
        for val in nodeValues:
            probs[val] = countValues[val] / len(matchingSamples)
        self.normalize(probs)
        return probs
        
        
        
    def selectConsistent(self, samples, evidence):
        """Given a list of samples (dictionaries) and an evidence dictionary,
        selects those samples whose values match the given evidence."""
        matchSamps = []
        for inst in samples:
            matches = True
            for node in evidence:
                if inst[node] != evidence[node]:
                    matches = False
            if matches:
                matchSamps.append(inst)
        return matchSamps

        
    # -----------------------------
    # Prior sampling
    
    def priorSampling(self, numSamples):
        """Given the number of samples to generate, this generates samples by
        iterating over the nodes in the network in topological order. For
        each node, it uses the previously-generated known values to do a
        weighted sampling of the current node's values given those
        previously-generated values. In the end it generates numSamples
        different instances of exam situations, and returns them as a list
        of dictionaries."""
        samples = []
        for i in range(numSamples):
            knowns = {}
            for node in self.nodeOrder:
                sampVal = self.sampleNode(node, knowns)
                knowns[node] = sampVal
            samples.append(knowns)
        return samples
            
        
        
        
    def sampleNode(self, node, knownDict):
        """Takes in a node name and a dictionary where the keys are nodes
        and the values are those nodes' known values. This gets the probabilities
        for this node consistent with the knowns, and then does a weighted
        sample from this node's values. It returns the value selected."""
        probs = []
        values = self.getNodeValues(node)
        for nodeVal in values:
            nextProb = self.lookupCPT(node, nodeVal, knownDict)
            probs.append(nextProb)
        return self.weightedSelection(values, probs)
    
    
    
    
    def weightedSelection(self, values, probs):
        """Given a list of values, and a corresponding list of probabilities, each
        value is associated with a probability. The probabilities should sum to 1.0.
        This function randomly selects one of the values and returns it, using the
        probabilities to weight the selection. This is essentially the same as the
        weighted roulette wheel selection we discussed for GAs."""
        tot = sum(probs)
        randVal = random.uniform(0, tot)
        sumProbs = 0
        for i in range(len(values)):
            sumProbs += probs[i]
            if sumProbs >= randVal:
                return values[i]
        assert False, "Shouldn't get here"
    




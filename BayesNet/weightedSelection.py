

import random



def weightedSelection(values, probs):
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
        
        
def normalize(probList):
    """Given a list of probabilities, re-scale them so that they add up to
    one (applying the alpha term to the distribution). Builds and returns
    a new list"""
    total = 0.0
    for prob in probList:
        total += prob
    normProbs = []
    for i in range(len(probList)):
        normProbs.append(probList[i] / total)
    return normProbs




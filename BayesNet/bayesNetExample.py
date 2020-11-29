

from bayesNetDef import *

# ================================================================
# The code below builds a Bayesian Network as specified in the
# file


network = BayesNet()

# filename = input("Enter filename to read from: ")
network.readBayesNet("examExample.txt")

# Call below computes conjunctive or conditional probability distributions
# prob distribution

while True:
    yorn = input("Shall we compute some probabilities? ")
    if yorn.lower() in ['n', 'no', 'q', 'quit', 'e', 'exit']:
        break
    network.askProbs()


priorSamps = network.priorSampling(1000)
print(priorSamps)
sleptEnoughSamps = [s for s in priorSamps if s['SleptEnough'] == 'True']
print(len(sleptEnoughSamps))
print("Probability that student slept enough =", len(sleptEnoughSamps) / 1000)


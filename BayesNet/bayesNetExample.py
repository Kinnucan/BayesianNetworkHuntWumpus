

from bayesNetDef import *

# ================================================================
# The code below builds a Bayesian Network as specified in the
# file


network = BayesNet()
networkHW = BayesNet()

# filename = input("Enter filename to read from: ")
network.readBayesNet("examExample.txt")
networkHW.readBayesNet("burglar.txt")


# Call below computes conjunctive or conditional probability distributions
# prob distribution

while True:
    yorn = input("Shall we compute some probabilities? ")
    if yorn.lower() in ['n', 'no', 'q', 'quit', 'e', 'exit']:
        break
    networkHW.askProbs()


priorSamps = network.priorSampling(1000)
print(priorSamps)
sleptEnoughSamps = [s for s in priorSamps if s['SleptEnough'] == 'True']
print(len(sleptEnoughSamps))
print("Probability that student slept enough =", len(sleptEnoughSamps) / 1000)

'''
P(RoommateInHouse | OpenDoor) = 0.21
P(RoommateInHouse | OpenDoor and CarInGarage) = 0.96
P(OpenDoor | DamagedDoor) = 0.10
P(RoommateInHouse | OpenDoor and not CarInGarage) = 0.01
'''


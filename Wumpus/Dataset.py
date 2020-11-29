"""Contains the Dataset class, which represents an ARFF-formatted dataset"""

import os

class Dataset:
    """A dataset is an object that contains the data from an ARFF file, organized to be
    used by other programs."""

    def __init__(self, filename):
        """Set up the dataset internal data, reading in the data from the file"""
        self.name = None
        self.attributes = {}
        self.attrOrder = []
        self.data = []
        try:
            f = open(filename)
        except:
            print("Unable to open the file!!")
        self.readArff(f)
        f.close()
        #self.printDataset()


    def readArff(self, fileObj):
        """Process the ARFF file, building up internal representations of
        the data."""
        startedData = False
        for row in fileObj:
            # print(row)
            if '%' in row:
                #print("Skipping comment:", row)
                pass
            elif '@relation' in row.lower():
                words = row.split()
                self.name = words[1]
                #print("Relation", self.name)
            elif '@attribute' in row.lower():
                words = row.split()
                attrName = words[1]
                attrVals = self.cleanAttrVals(words[2:])
                #print("Attribute  name:", attrName, "   values:", attrVals)
                self.attributes[attrName] = attrVals
                self.attrOrder.append(attrName)
            elif '@data' in row.lower():
                #print("Starting data")
                startedData = True
            elif not startedData:
                #print("Skipping line:", row)
                pass
            elif row.isspace() or row == "":  # from previous tests, we know that we've started the data portion
                #print ("End of file")
                pass
            else:
                row = row.strip()
                words = row.split(",")
                if len(words) != len(self.attrOrder):
                    print("PROBLEM: mismatch between number of data values and attributes")
                    print(row)
                else:
                    dataInst = {}
                    for i in range(len(words)):
                        dataInst[self.attrOrder[i]] = words[i].strip()
                    self.data.append(dataInst)


    def cleanAttrVals(self, words):
        """Takes a list of attribute values, and cleans them up. It removes
        curly braces and commas, and splits up strings where a comma is in the 
        middle (in case input file didn't have spaces after every comma."""
        newWords = []
        for i in range(len(words)):
            word = words[i]
            word = word.strip("{,} ")
            if ',' in word:
                moreWords = word.split(',')
                moreCleanWords = self.cleanAttrVals(moreWords)
                newWords.extend(moreCleanWords)
            elif word != "":
                newWords.append(word)
        return newWords
        

    def printDataset(self):
        """Print the dataset in a readable format"""
        print("Dataset:", self.name)
        print("-------------------------")
        print("Attributes:")
        for attName in self.attrOrder:
            print("  " + attName + ":  ",  end="")
            for val in self.attributes[attName]:
                print(val, end="")
            print()
        print("=========================")
        print("Data:")
        astr = " " * 5
        for attName in self.attrOrder:
            astr += ("%15s" % attName)
        print(astr)
        print("-" * len(astr))
        for i in range(len(self.data)):
            print("%4d" % i, end="")
            inst = self.data[i]
            dstr = ""
            for attr in self.attrOrder:
                dstr += "%15s" % self.data[i][attr]
            print(dstr)
        
    def getAttributes(self):
        """Return a list of attributes"""
        return self.attrOrder

    def getAttrValues(self, attr):
        """Given an attribute, returns the list of values associated with it."""
        return self.attributes.get(attr, None)
    
    def getName(self):
        """Return the category name for this dataset."""
        return self.name
    
    
    def computePriors(self):
        """Return a dictionary containing prior probabilities for all
        attributes and values in the dataset."""
        priorProbs = {}
        for attrName in self.attrOrder:
            attrProbs = []
            for attrVal in self.attributes[attrName]:
                attrProbs.append(self.getPriorFor(attrName, attrVal))
            priorProbs[attrName] = attrProbs
        return priorProbs



    def getPriorFor(self, attribute, value):
        """Given an attribute and value, compute the prior probability 
        P(attribute = value) from the dataset."""
        popSize = len(self.data)
        count = 0
        for inst in self.data:
            if inst[attribute] == value:
                count = count + 1
        prior = float(count) / popSize
        return prior




    def getConditionalFor(self, attr1, val1, givenAttr, givenVal):
        """Inputs are an attribute and value, and a given attribute and value,
        this computes P(attr1 = val1 | givenAttr = givenVal) from the dataset."""
        subsetSize = 0
        count = 0
        for inst in self.data:
            if inst[givenAttr] == givenVal:  # if inst belongs to this group
                subsetSize += 1              # add one to the size of the group
                if inst[attr1] == val1:      # and if also has the conditional attr
                    count += 1               # add one to that count
        if subsetSize > 0:
            probab = float(count) / subsetSize
        else:
            probab = 0
        return probab



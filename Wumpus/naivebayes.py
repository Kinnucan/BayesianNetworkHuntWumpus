""" Defines a NaiveBayes network"""

import Dataset



class NaiveBayes:
    """Builds a Naive Bayes network. The network is built based on a dataset, using the Dataset
    class which reads ARFF files. The network has an input for each value of each attribute
    in the dataset, and an output for each value of the classifier attribute."""
    
    
    def __init__(self, mode="dataset", networkFile=None, dataset=None, category=None):
        """Reads data either from a file that describes the network, or takes in a Dataset object
        and constructs the network from the dataset.
        It sets up output probability holders, and computes the weights for each input/output pair."""
        self.dataset = dataset
        self.category = category
        self.networkFilename = networkFile
        self.outputValues = []
        self.outputInitProbs = dict()
        self.outputCurrProbs = dict()
        self.outputNormProbs = dict()
        self.inputsOn = dict()
        self.weights = dict()
        self.varieties = dict()
        self.attributes = []

        if mode == "dataset":
            if self.dataset is None:
                print("ERROR in NaiveBayes: if mode is dataset, a dataset must be provided!")
                return
            else:
                self._buildFromDataset()
        elif mode == 'file':
            if self.networkFilename is None:
                print("ERROR in NaiveBayes: if mode is file, then a filename must be provided!")
                return
            else:
                self._buildFromFile()

    def _buildFromFile(self):
        """Reads the description of a network from a file."""
        filObj = open(self.networkFilename, 'r')
        stage = 'output name'
        currAttribute = None
        for line in filObj:
            if line.strip() == "" or line[0] == '#':
                continue
            lineParts = line.split()
            label = lineParts[0].lower()
            if label == 'outputs' and stage == 'output name':
                self.category = lineParts[1]
                stage = 'output values'
            elif label == 'value' and stage == 'output values':
                valueName = lineParts[1]
                prior = float(lineParts[2])
                self.outputValues.append(valueName)
                self.outputInitProbs[valueName] = prior
                self.outputCurrProbs[valueName] = prior
                self.outputNormProbs[valueName] = prior
            elif label == "inputs" and stage == 'output values':
                stage = "input attributes"
            elif label == 'attribute' and stage == 'input attributes':
                currAttribute = lineParts[1]
                self.attributes.append(currAttribute)
                self.varieties[currAttribute] = []
            elif label == 'value' and stage == 'input attributes' and currAttribute is not None:
                valueName = lineParts[1]
                probs = [float(s) for s in lineParts[2:]]
                attrPrior = probs[-1]
                condProbs = probs[:-1]  # all but last one
                self.varieties[currAttribute].append(valueName)
                self.inputsOn[currAttribute, valueName] = False
                if len(condProbs) != len(self.outputValues):
                    print("ERROR: wrong number of conditional probabilities:", line)
                for i in range(len(condProbs)):
                    outName = self.outputValues[i]
                    condProb = condProbs[i]
                    if attrPrior == 0.0:
                        self.weights[currAttribute, valueName, outName] = 1.0
                    else:
                        weightVal = condProb / attrPrior
                        self.weights[currAttribute, valueName, outName] = weightVal
            else:
                print("ERROR: something is wrong here")
                print("   stage =", stage)
                print("   line =", line)





    def _buildFromDataset(self):
        """Builds the network from the data in the dataset."""
        if self.category is None:
            self.category = self.dataset.getName()
        priors = self.dataset.computePriors()
        outputPriors = priors[self.category]
        self.outputValues = self.dataset.getAttrValues(self.category)
        for i in range(len(self.outputValues)):
            self.outputInitProbs[self.outputValues[i]] = outputPriors[i]
            self.outputCurrProbs[self.outputValues[i]] = outputPriors[i]
            self.outputNormProbs[self.outputValues[i]] = outputPriors[i]

        for attribute in self.dataset.getAttributes():
            if attribute != self.category:
                self.attributes.append(attribute)
                pos = 0
                self.varieties[attribute] = self.dataset.getAttrValues(attribute)
                for attrVal in self.varieties[attribute]:
                    self.inputsOn[attribute, attrVal] = False
                    attrValPrior = priors[attribute][pos]
                    for oVal in self.outputValues:
                        if attrValPrior == 0.0:
                            self.weights[attribute, attrVal, oVal] = 1.0
                        else:
                            conditProb = self.dataset.getConditionalFor(attribute, attrVal, self.category, oVal)
                            self.weights[attribute, attrVal, oVal] = conditProb / attrValPrior
                    pos += 1
    
    
    def getCategory(self):
        """Returns the name of the category"""
        return self.category

    def getOutputNames(self):
        """Returns a list of the values associated with the output category,
        the outcomes"""
        return self.outputValues[:]
    
    def getAttributes(self):
        """Returns a list of the attributes from the dataset that are inputs to
        the network"""        
        return self.attributes[:]
    
    def getAttributeValues(self, attribute):
        """Given an attribute, returns the value of that attribute, or None
        if no attribute exists."""
        dataList = self.varieties.get(attribute, [])
        return dataList[:]
    
    def getCurrentOutputProb(self, outputName):
        """Given an output value, report the current output probability.
        Returns None if bad input."""
        return self.outputCurrProbs.get(outputName, None)
    
    def getNormedOutputProb(self, outputName):
        """Given an output value, report the current normalized output probability.
        Returns None if bad input."""
        return self.outputNormProbs.get(outputName, None)
    
    def getWeightValue(self, attribute, attrValue, outputName):
        """Given an attribute, value, and output, report the weight between
        them. Return None if bad input."""
        return self.weights.get((attribute, attrValue, outputName), None)
    
    def getInputStatus(self, attribute, attrValue):
        """Given an attribute and value, report whether it is set on or not.
        Returns None if bad input."""
        return self.inputsOn.get((attribute, attrValue), None)
    


    def resetNetwork(self):
        """Resets the output probabilities to the prior probabilities, and 
        sets all inputs as off."""
        for outVal in self.outputCurrProbs:
            self.outputCurrProbs[outVal] = self.outputInitProbs[outVal]
        for node in self.inputsOn:
            self.inputsOn[node] = False



    def recomputeOutputs(self):
        """Given the current set of features that are turned on in the input,
        this should update the output "probabilities" of the network."""
        for outVal in self.outputCurrProbs:
            currProb = self.outputInitProbs[outVal]
            for attr in self.attributes:
                for attrVal in self.varieties[attr]:
                    if self.inputsOn[attr, attrVal]:
                        currProb = currProb * self.weights[attr, attrVal, outVal]
            self.outputCurrProbs[outVal] = currProb
        self.normalizeOutputs()
                
    
    
    def setFeature(self, attribute, attrValue):
        """Given an attribute and value, set it to be "on" and recalculate 
        the output to take into account this feature"""
        if self.inputsOn[attribute, attrValue] != None:
            self.inputsOn[attribute, attrValue] = True
            self.recomputeOutputs()
            self.normalizeOutputs()


    def unsetFeature(self, attribute, attrValue):
        """Given an attribute and value, set it to be "off" and recalculate
        the output probabilities to take the change into account."""
        if self.inputsOn[attribute, attrValue] != None:
            self.inputsOn[attribute, attrValue] = False
            self.recomputeOutputs()
            self.normalizeOutputs()


    def normalizeOutputs(self):
        """Normalize the output probabilities so that they sum to 1.0"""
        sumVal = 0.0
        for outVal in self.outputCurrProbs:
            sumVal += self.outputCurrProbs[outVal]
        if sumVal > 0:
            for outVal in self.outputNormProbs:
                self.outputNormProbs[outVal] = self.outputCurrProbs[outVal] / sumVal
            
                
    
    def printNetwork(self):
        """Print the current network in a readable format"""
        for categVal in self.getOutputNames():
            print("============ Output ============" )
            print("%10s: %15s%15s" % (categVal, "Raw", "Normalized"))
            currProb = self.getCurrentOutputProb(categVal)
            normProb = self.getNormedOutputProb(categVal)
            print("%10s  %15.2f%15.2f" % ("", currProb, normProb))
            print()
            for attribute in self.getAttributes():
                for inpValue in self.getAttributeValues(attribute):
                    print("%10s" % attribute, end="")
            print()
            for attribute in self.getAttributes():
                for inpValue in self.getAttributeValues(attribute):
                    print( "%10.2f" % self.getWeightValue(attribute, inpValue, categVal), end="")
            print()
            for attribute in self.getAttributes():
                for inpValue in self.getAttributeValues(attribute):
                    print("%10d" % self.getInputStatus(attribute, inpValue), end="")
            print()              
            for attribute in self.getAttributes():
                for inpValue in self.getAttributeValues(attribute):
                    print("%10s" % inpValue, end="")
            print()
        
# ------------------------------------------------------------------



if __name__ == "__main__":
    print("===============================================================================")
    print("Demo 1: reading network from a file...")
    nb1 = NaiveBayes('file', networkFile="findPit8by8.txt")
    nb1.printNetwork()


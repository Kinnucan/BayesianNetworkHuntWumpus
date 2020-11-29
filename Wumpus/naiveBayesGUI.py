from tkinter import*
import tkinter.filedialog
import naivebayes
import Dataset
import string


class naiveBayesGUI:
    
    
    
    def __init__(self):
        self.root = Tk()
        self.root.title("Naive Bayes")
        
        
    def setupWidgets(self):
        
        #Create the top panel, containing load, quit and help buttons.
        self._initBasicControls()
        
        
        
    def goProgram(self):
        self.root.mainloop()
        
        
        
    #########################################
    #Create the widgets

    ###Basic Control Frame
    def _initBasicControls(self):
        basicControlFrame = Frame(self.root, bd = 5, padx = 5, pady = 5, relief = "groove")
        basicControlFrame.grid(row = 1, column = 1)
        basicControlFrameTitle = Label(basicControlFrame, text = "Naive Bayes Calculation", font = "Arial 14 bold", padx = 5, pady = 5)
        basicControlFrameTitle.grid(row = 0, column = 1)
        
        #Help and quit Buttons
        masterHelpButton = Button(basicControlFrame, text = "Help", command = self.openHelpMenu)
        masterHelpButton.grid(row = 0, column = 2)
        masterQuitButton = Button(basicControlFrame, text = "Quit", command = self.masterQuit)
        masterQuitButton.grid(row = 0, column = 3)

        #Load Button
        masterLoadButton = Button(basicControlFrame, text = "Load", command = self.masterLoad)
        masterLoadButton.grid(row = 1, column = 1, pady=10, padx=10)


        #Two variables used by the load operation, one to display the currently loaded file, the other to store it for later use. 
        self.displayMasterLoaded = StringVar()
        self.displayMasterLoaded.set("no file loaded")
        self.masterLoaded = StringVar()
        self.masterLoaded.set("no file loaded")
        masterCurrentLoaded = Label(basicControlFrame, textvariable = self.displayMasterLoaded, font = "Arial 12", padx = 5, pady = 0)
        masterCurrentLoaded.grid(row = 1, column = 2, columnspan = 2)

        self.whichLoad = StringVar()
        arffButton = Radiobutton(basicControlFrame, variable = self.whichLoad, text = "Load dataset (ARFF)", value = "dataset")
        arffButton.grid(row=2, column = 1)

        savedButton = Radiobutton(basicControlFrame, variable=self.whichLoad, text = "Load network file", value = "file")
        savedButton.grid(row=2, column=2)

        #Error Output
        self.errorMessage = StringVar()
        loadErrorOutputLabel = Label(basicControlFrame, textvariable = self.errorMessage, font = "Arial 12", padx = 5, pady = 0)
        loadErrorOutputLabel.grid(row=10, column = 1)
        
        self._makeNetworkFrames()


    def _makeNetworkFrames(self):
        """Makes the outcomeSelectFrame, which has to be recreated every time we load a file."""
        self.outcomeSelectFrame = Frame(self.root, bd = 5, padx = 5, pady = 5, relief ="groove")
        self.outcomeSelectFrame.grid(row = 2, column = 1, padx=10, pady=10)
        self.mainDisplayFrame = Frame(self.root, bd = 5, padx = 5, pady = 5, relief = "groove")
        self.mainDisplayFrame.grid(row = 3, column = 1)

        
    ####Basic Control Frame Button Commands
    
    #Help Menu Button Command
    def openHelpMenu(self):
       
        self.helpWindow = Toplevel()
        helpTxt = """Load: Loads in a dataset from an ARFF file, building a Naive Bayes network from it
        Start Over: Unloads the dataset and destroys the Naive Bayes Network
        Quit: Quits the program
        Once a dataset is loaded:
        Select which outcome's weights to see by selecting the outcome's radio button
        Select an attribute's value to see the effect of that value on the outcomes
        """
        
        textField = Label(self.helpWindow, text = helpTxt, padx = 10, pady = 10, justify = LEFT)
        closeButton = Button(self.helpWindow, text = "Close", command = self.closeHelp)
        textField.grid(row = 1, column = 1)
        closeButton.grid(row = 2, column = 1)
    
        
    #This closes the Help Window
    def closeHelp(self):
        self.helpWindow.destroy()
        
        
     #Quits the program
    def masterQuit(self):
        self.root.destroy()
    
    #Loads the file
    def masterLoad(self):
        """Asks the user to select a filename of the appropriate type, then it creates the naive bayes
        network, and displays it."""
        print(self.whichLoad.get())
        if self.whichLoad.get() == 'dataset':
            prompt = "Load a .ARFF file"
        else:
            prompt = "Load a saved network file"
        fileOkay, filename = self._getFilename(prompt)
        print(fileOkay, filename)
        if fileOkay:
            self.clearCurrent()
            tempFilename = self.shortenFileName(filename)
            self._setDisplayMasterLoaded(tempFilename)
            self._setMasterLoaded(filename)
            if self.whichLoad.get() == 'dataset':
                print("Loading dataset")
                self.tempDataset = Dataset.Dataset(filename)
                self.network = naivebayes.NaiveBayes(mode="dataset", dataset=self.tempDataset)
            else:
                self.network = naivebayes.NaiveBayes("file", networkFile=filename)

            # Create the outcome selection frame
            self._initOutcomeSelect()

            # Create the main display frame
            self._initMainDisplay()


    def _getFilename(self, promptString):
        """Pops up a dialog box to ask the user for a filename, returns a boolean if the file was chosen well,
        and the name/path of the file. Otherwise, returns an empty string and a boolean False."""
        try:
            filename = tkinter.filedialog.askopenfilename(title=promptString)
            self.errorMessage.set("")
        except:
            self.errorMessage.set("incorrect filename")
            return False, ""
        if filename == "":
            return False, ""
        return True, filename

    #Clears the cent information
    def clearCurrent(self):
        """Clears the information about the network from the outcome frame and the main display frame"""
        for frame in [self.outcomeSelectFrame, self.mainDisplayFrame]:
            children = frame.winfo_children()
            for kidWidget in children:
                kidWidget.destroy()


    ###Outcome Selection Frame
    def _initOutcomeSelect(self):
        self.currentOutcome = StringVar()
        self.outcomeList = self.network.getOutputNames() 
        numberOfOutcomes = len(self.outcomeList)

        outcomeSelectFrameTitle = Label(self.outcomeSelectFrame, text = "Outcomes for category " + self.network.getCategory(),
                                        font = "Arial 16 bold", padx = 5, pady = 5)
        outcomeSelectFrameTitle.grid(row = 0, columnspan = numberOfOutcomes + 1)
        instr = Label(self.outcomeSelectFrame, text = "Select outcome to see weights from features",
                      font = "Arial 10", padx = 5, pady = 5)
        instr.grid(row = 1, columnspan = numberOfOutcomes + 1)
        
        ### Outcome Selection Buttons
        outcomeButtonList = []
        rawProbLabels = []
        normProbLabels = []
        self.rawProbText = []
        self.normProbText = []
        

        outcomeLabel = Label(self.outcomeSelectFrame, text = "Outcome:", font = "Arial 12 bold", padx = 5, pady = 5)
        outcomeLabel.grid(row = 2, column = 0)
        probLabel = Label(self.outcomeSelectFrame, text = "Raw Prob:", font = "Arial 12 bold", padx = 5, pady = 5)
        probLabel.grid(row = 3, column = 0)
        normLabel = Label(self.outcomeSelectFrame, text = "Norm Prob:", font = "Arial 12 bold", padx = 5, pady = 5)
        normLabel.grid(row = 4, column = 0)
        #For loop to generate the outcome select buttons based on the dataset.
        for outcome in self.outcomeList:   
            newRadioButton = Radiobutton(self.outcomeSelectFrame, variable = self.currentOutcome, text = outcome, value = outcome, command = self.changeOutput)
            outcomeButtonList.append(newRadioButton)

            rawProbString = StringVar()
            printable = self.formatString(self.network.getCurrentOutputProb(outcome))
            rawProbString.set(printable)
            outcomeRawProbLabel = Label(self.outcomeSelectFrame, textvariable = rawProbString, font = "Arial 12", padx = 5, pady = 5)
            self.rawProbText.append(rawProbString)
            rawProbLabels.append(outcomeRawProbLabel)

            normProbString = StringVar()
            printable = self.formatString(self.network.getNormedOutputProb(outcome))
            normProbString.set(printable)
            outcomeNormProbLabel = Label(self.outcomeSelectFrame, textvariable = normProbString, font = "Arial 12", padx = 5, pady = 5)
            self.normProbText.append(normProbString)
            normProbLabels.append(outcomeNormProbLabel)
            
        # For loop to place the buttons that were just generated
        for i in range (0, numberOfOutcomes):
            outcomeButton = outcomeButtonList[i]
            outcomeButton.grid(row = 2, column = i+1)
            rawProbLabel = rawProbLabels[i]
            rawProbLabel.grid(row = 3, column = i+1)
            normProbLabel = normProbLabels[i]
            normProbLabel.grid(row = 4, column = i+1)
        self.currentOutcome.set(self.outcomeList[0])  
     
    ###Attribute Selection Frame Button commands


    #This changes the output numbers for the outcomes in the outcome selection frame
    def changeOutput(self):
        for x in range (0, len(self.attributeList)):
            currentColumn  = self.attributeList[x]
            tempColumn = self.attributeNumberStrings[x]
            for y in range(1, len(currentColumn)):  
                numberToBeChanged = tempColumn[y-1]
                newNumber = self.network.getWeightValue(currentColumn[0], currentColumn[y], self.currentOutcome.get())
                newNumber = self.formatString(newNumber)
                numberToBeChanged.set(newNumber)
            
        
    ###Main Display Frame

    def _initMainDisplay(self):
        #These commands place the main display frame, and the toggles for the different variables which can be included.
        tempAttributeList = self.network.getAttributes()
        self.attributeList = []
        self.attributeNumbers = []
        #This loop gathers the information from the data set to be passed on to the "constructMainDisplay" function.
        for attribute in tempAttributeList:
            tempAttributeItem = self.network.getAttributeValues(attribute)
            tempNumberList = []
            for item in tempAttributeItem:
                
                tempNumber = self.network.getWeightValue(attribute, item, self.currentOutcome.get())
                tempNumberList.append(tempNumber)
            self.attributeNumbers.append(tempNumberList)
            tempAttributeItem.insert(0, attribute)
            self.attributeList.append(tempAttributeItem)
            
        
        self.numberOfAttributes = len(self.attributeList)
        self.constructMainDisplay(self.attributeList, self.numberOfAttributes, self.attributeNumbers)
        
    # This function constructs the main display, and places all the buttons based on the info given to it,
    def constructMainDisplay(self, attributeList, numberOfAttributes, attributeNumbers):
        self.attributeNumberStrings = []
        #The following loops gather all the information needed from the dataset, and then they construct the checkbox items which allow for an attribute to be selected.
        for i in range(0, self.numberOfAttributes):
            currAttrFrame = Frame(self.mainDisplayFrame, bd = 1, bg = "lightyellow", padx = 10, pady = 10, relief = "groove")
            currAttrFrame.grid(row = 0, column = i, sticky="N")
            currentAttributeInfo = self.attributeList[i]
            newAttributeLabel = Label(currAttrFrame, text = currentAttributeInfo[0], font = "Arial 16 bold", padx = 5, pady = 5)
            newAttributeLabel.grid(row = 0, column = 0)
            columnAttributeNumbers = []
            for j in range(1, len(currentAttributeInfo)):
                valueFrame = Frame(currAttrFrame, padx = 5, pady = 5, relief = "groove")
                valueFrame.grid(row = j, column = 0, padx = 5, pady = 5)
                currentOutcome = currentAttributeInfo[j]
                newoutcomeLabel = Label(valueFrame, text = currentOutcome, font = "Arial 12 bold", padx = 5, pady = 5)
                newoutcomeLabel.grid(row = (5 * j),  column = 0)
                checkButtonVar = IntVar()
                callback = self.makeCommand(checkButtonVar, currentAttributeInfo[0] ,currentOutcome)
                newCheckButton = Checkbutton(valueFrame, 
                                             variable = checkButtonVar, 
                                             command = callback)
                newCheckButton.var = checkButtonVar
                newCheckButton.grid(row = (5 * j) + 1, column = 0)
                currentAttributeNumbers = attributeNumbers[i]
                currentAttributeNumber = currentAttributeNumbers[j-1]
                numberVariable = StringVar()
                currentAttributeNumber = self.formatString(currentAttributeNumber)
                numberVariable.set("w = " + currentAttributeNumber)
                newNumberLabel = Label (valueFrame, textvariable = numberVariable, font = "Arial 10", padx = 5, pady = 5)
                newNumberLabel.grid(row = (5 *j) + 2, column = 0)
                
                columnAttributeNumbers.append(numberVariable)
            self.attributeNumberStrings.append(columnAttributeNumbers)
        
                
                
                
            
   
            
        
        
        
        
        
    ###Getters and Setters
    #Sets the display for what file has been loaded
    def _setDisplayMasterLoaded(self, fileName):
        self.displayMasterLoaded.set(fileName)
    
        
    #Sets the file that has been loaded.
    def _setMasterLoaded(self, fileName):
        self.masterLoaded.set(fileName)
    
        
        
        
    #####Utility Functions
    
    #This function creates a command for the checkboxes, so that way they will be able to update the values when one is checked or unchecked.
    def makeCommand(self, intVar, attribute, value):
        def command():
            currentVariable = intVar.get()
            if currentVariable == 1:
                self.network.setFeature(attribute, value)
            else:
                self.network.unsetFeature(attribute, value)
            for i in range(0 , len(self.outcomeList)):
                currOutcome = self.outcomeList[i]
                currentProb = self.network.getCurrentOutputProb(currOutcome)
                rawProbStr = self.formatString(currentProb)
                self.rawProbText[i].set(rawProbStr)
                normedProb = self.network.getNormedOutputProb(currOutcome)
                normedProbStr = self.formatString(normedProb)
                self.normProbText[i].set(normedProbStr)
                
        ####
        return command
    
    
    #This shortens the filename of the loaded file.
    def shortenFileName(self, fileName):
        l = len(fileName)
        f = "..." + fileName[l-35:]
        return f
    
    #This function takes a number and shortens it to only 4 decimal places. Ex 4.xxxx
    def formatString(self, num):
        template = "{0:1.3f}"
        newString = template.format(num)
        return newString
############################################################        
#Run the program 

def Run():
    s = naiveBayesGUI()
    s.setupWidgets()
    s.goProgram()
    
if __name__ == "__main__":
    Run()
        
"""    Written by Samuel Solomon        --------------------------------------------------------------------------    Data Aquisition:        All channels were placed on the right arm    Channel 1 (bottom channel of the arduino used in this experiment) represents    the EMG signal from the muscle located on top of the arm (with the hand facing     palm down). For clarity, this is the muscle that moves the most when the wrist    is flexed up (with the palm of the hand facing resting on the table)    Channel 2 (second lowest on arduino) is to the right of channel one on the arm    with respect to the user looking directly at the hand (away from thumb)        --------------------------------------------------------------------------        Modules to Import Before Running the Program (Some May be Missing):        $ conda install matplotlib        $ conda install tensorflow        $ conda install openpyxl        $ conda install sklearn        $ conda install joblib        $ conda install numpy        $ conda install keras            --------------------------------------------------------------------------"""# Basic Modulesimport sysimport numpy as np# Neural Network Modulesfrom sklearn.model_selection import train_test_split# Import Data Aquisition and Analysis Filessys.path.append('./Data Aquisition and Analysis/')  # Folder with Data Aquisition Filesimport readDataExcel as excelData       # Functions to Save/Read in Data from Excelimport readDataArduino as streamData    # Functions to Read in Data from Arduino# Import Machine Learning Filessys.path.append('./Machine Learning Modules/')  # Folder with Machine Learning Filesimport neuralNetwork as NeuralNet       # Functions for Neural Networkimport KNN as KNN                       # Functions for K-Nearest Neighbors' Algorithmif __name__ == "__main__":    # ---------------------------------------------------------------------- #    #    User Parameters to Edit (More Complex Edits are Inside the Files)   #    # ---------------------------------------------------------------------- #    # General Data Collection Information (You Will Likely Not Edit These)    arduinoSerialNum = '85735313333351E040A0'  # Arduino's Serial Number (port.serial_number)    numDataPoints = 80000  # The Number of Points to Stream into the Arduino    moveDataFinger = 200   # The Number of Data Points to Plot/Analyze at a Time    numChannels = 4        # The Number of Arduino Channels with EMG Signals Read in    xWidth = 2000          # The Number of Data Points to Display to the User at a Time        # Protocol Switches: Only One Can be True; Only the First True Variable Excecutes    streamArduinoData = False  # Stream in Data from the Arduino and Analyze    readDataFromExcel = True  # Analyze Data from Excel File called 'testDataExcelFile', specifically using Sheet 'testSheetNum'    reAnalyzePeaks = False     # Read in ALL Data Under 'trainDataExcelFolder', and Reanalyze Peaks    trainModel = False          # Read in ALL Data Under 'neuralNetworkFolder', and Train the Data        # User Option During the Run    saveInputData = False # Saves the Data Streamed in as 'saveExcelName'    seeFullPlot = True    # Graph the Peak Analysis IN ADDITION TO the Arduino Data    SaveModel = False     # Save the Machine Learning Model for Later Use        # ---------------------------------------------------------------------- #        # Take Data from the Arduino and Save it as an Excel (For Later Use)    if saveInputData:        saveExcelName = "Samuel Solomon 2021-03-18.xlsx"  # The Name of the Saved File        saveDataFolder = "../Input Data/Training Data/"   # Data Folder to Save the Excel Data; MUST END IN '/'        handMovement = "Release"                          # Speficy the hand Movement You Will Perform                sheetName = "Trial 1 - "  # If SheetName Already Exists, Excel 1 to Trial #        sheetName = sheetName + handMovement        # Instead of Arduino Data, Use Test Data from Excel File    if readDataFromExcel:        testDataExcelFile = "../Input Data/Test Data/channel.xlsx" # Path to the Test Data        testSheetNum = 0                     # The Sheet/Tab Order (Zeroth/First/Second/Third) on the Bottom of the Excel Document        # Use Previously Processed Data that was Saved; Extract Features for Training    if reAnalyzePeaks or trainModel:        trainDataExcelFolder = "../Input Data/Training Data/"  # Path to the Training Data Folder; All .xlsx Data Used        if trainModel:        # Pick the Machine Learning Module to Use        applyNN = False        applyKNN = True        # Initialize Machine Learning Parameters/Data        modelPath = "./Machine Learning Modules/Models/myModel.pkl"    # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #    #           Initiate Neural Network (Should Not Have to Edit)            #    # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #        # Define Labels as Array    movementOptions = np.array(["Right", "Left", "Up", "Down", "Grab", "Release"])    movementOptions = np.char.lower(movementOptions)    # Edge Case: User Defines a Movement that Does not Exist, Return Error    if saveInputData and handMovement.lower() not in movementOptions:        print("\nUser Defined an Unknown Hand Gesture")        print("The Gesture", "'" + handMovement.lower() + "'", "is Not in", movementOptions)        sys.exit()        if trainModel:        # Make the Neural   (dim = The dimensionality of one data point)         if applyNN:            MLModel = NeuralNet.Neural_Network(modelPath = modelPath, dataDim = numChannels)        elif applyKNN:            MLModel = KNN.KNN(modelPath = modelPath, numClasses = len(movementOptions))    else:        MLModel = None            # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #    #           Data Collection Program (Should Not Have to Edit)            #    # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #              # Stream in Data from Arduino (EMG Signals)    if streamArduinoData:        readData = streamData.arduinoRead(xWidth, moveDataFinger, numChannels, movementOptions)        readData.streamArduinoData(numDataPoints, arduinoSerialNum, seeFullPlot, myModel = MLModel)    # Take Data from Excel Sheet    elif readDataFromExcel:        readData = excelData.readExcel(xWidth, moveDataFinger, numChannels, movementOptions)        readData.streamExcelData(testDataExcelFile, seeFullPlot, testSheetNum, myModel = MLModel)    # Redo Peak Analysis    elif reAnalyzePeaks:        readData = excelData.readExcel(xWidth, moveDataFinger, numChannels, movementOptions)        readData.getTrainingData(trainDataExcelFolder, movementOptions, mode='reAnalyze')    # Take Preprocessed (Saved) Features from Excel Sheet    elif trainModel:        readData = excelData.readExcel(xWidth, moveDataFinger, numChannels, movementOptions)        signalData, signalLabels = readData.getTrainingData(trainDataExcelFolder, movementOptions, mode='Train')        print("\nCollected Signal Data")        # Save the Data in Excel: EMG Channels (Cols 1-4); X-Peaks (Cols 5-8); Peak Features (Cols 9-12)    if saveInputData:        saveInputs = excelData.saveExcel(numChannels)        verifiedSave = input("Are you Sure you Want to Save the Data (Y/N): ")        if verifiedSave.upper() == "Y":            saveInputs.saveData(readData.data, readData.xTopGrouping, readData.featureSetGrouping, saveDataFolder, saveExcelName, sheetName, handMovement)        else:            print("User Chose Not to Save the Data")        # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #    #                    Train the Machine Learning Model                    #    # ---------------------------------------------------------------------- #    # ---------------------------------------------------------------------- #        # Train the ML    if trainModel:        # Split the Data into Training and Validation Sets        Training_Data, Testing_Data, Training_Labels, Testing_Labels = train_test_split(signalData, signalLabels, test_size=0.2, shuffle= True, stratify=signalLabels)                if applyKNN:            # Format Labels into 1D Array (Needed for KNN Setup)            Training_LabelsKNN = [np.argmax(i) for i in Training_Labels]            Testing_LabelsKNN = [np.argmax(i) for i in Testing_Labels]            signalLabelsKNN = [np.argmax(i) for i in signalLabels]            # Train the NN with the Training Data            MLModel.trainModel(Training_Data, Training_LabelsKNN, Testing_Data, Testing_LabelsKNN)            # Plot the training loss                MLModel.plotModel(signalData, signalLabelsKNN)        if applyNN:            # Train the NN with the Training Data            MLModel.trainModel(Training_Data, Training_Labels, Testing_Data, Testing_Labels, 500, seeTrainingSteps = False)            # Plot the training loss                MLModel.plotModel()        # Save the Neural Network (The Weights of Each Edge)        if SaveModel:            MLModel.saveModel(modelPath)
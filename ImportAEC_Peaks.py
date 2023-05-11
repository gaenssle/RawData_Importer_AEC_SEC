#!/usr/bin/python
# The script has been written in Python 3.5
# Script written by ALO Gaenssle, August 2019

import os


#####################################################################
# FUNCTIONS
#####################################################################

# Get name of folder that contains the files to be imported
def GetFolderName(DirectoryName):
	print("\n","-"*75,"\n","-"*75,"\n")
	print("\tAEC PEAK IMPORTER \t\tby A.L.O. Gaenssle, 2019")
	print("\n","-"*75,"\n","-"*75)
	InputPath = input("\nEnter the folder name containing "
		"the files to be imported"
		"\n\nYour current directory is:\n%s"
		"\n\n- If it is a subfolder of the above enter: e.g. FOLDER"
		"\n- Otherwise enter full path: e.g. X:\Experiments\FOLDER\n"
		% DirectoryName)
	while os.path.exists(os.path.abspath(InputPath)) == False:
		InputPath = input("\nThis folder does not exist!"
			"\nPlease enter a correct name"
			"\n(Check the file path by right clicking on "
			"the folder and selecting 'Properties')"
			"\n(Use arrows on keyboard for faster correction)\n")
	return (InputPath)

# Get the names of the files in the folder
def GetFileList(InputPath):
	FileList = []
	for FileName in os.listdir(os.path.abspath(InputPath)):
		if  FileName.endswith(".txt") or FileName.endswith(".TXT") \
			and not FileName in FileList:
			FileList.append(FileName)
			print(FileName)
	FilesCorrect = input("\nAre these files correct?\n"
		"(y=yes, n=no)\n")
	while FilesCorrect not in ("y", "n"):
			FilesCorrect = input("\nPlease enter 'y' or 'n'!\n")
	return(FilesCorrect, FileList)

def GetValues():
	Correct = False
	while Correct == False:
		try:
			MinArea = float(input("\nEnter the minimun Area (nC*min)"
				"\n-> only export peaks with areas larger than that"
				"\n(default=1.0)\n"))
		except ValueError:
			print("\nPlease enter a number!")
		else:
			break
	while Correct == False:
		try:
			MinTime = float(input("\nEnter the minimun Time (min)"
				"\n-> only export peaks eluted after that time"
				"\n(default=2.3)\n"))
		except ValueError:
			print("\nPlease enter a number!")
		else:
			break
	while Correct == False:
		try:
			RoundTime = 1/float(input("\nEnter the round Time (min)"
				"\n-> compensate for small time shifts"
				"\n(default=0.2)\n"))
		except ValueError:
			print("\nPlease enter a number!")
		else:
			break
	return(MinArea, MinTime, RoundTime)

# Subfunction of ImportFiles and sub-sub-function of GetData
# Append data to the dictionaries
def AddData(Index, Time, Data, Signal):
	if Time in Data:
		if len(Data[Time]) <= Index:
			SignalList = [""]*(Index-len(Data[Time]))
			Data[Time].extend(SignalList)
			Data[Time].append(Signal)
		elif Signal > Data[Time][Index]:
			Data[Time][Index] = Signal
	else:
		SignalList = [""]*Index
		Data.update({Time:SignalList})
		Data[Time].append(Signal)
	return(Data)

# Sub-function of GetData
# Import the data from each file
def ImportFiles(FileName, MinArea, MinTime, RoundTime, Index, 
	SampleList, AreaData, HeightData, RelAreaData, PeakTypeData):
	InsideData = False
	for Line in open(FileName, 'r'):
		Line= Line.rstrip()
		if InsideData == False:
			if Line.startswith("Injection Name:\t"):
				Line = Line.split('\t')[2]
				SampleList.append(Line)				
			elif Line == "Integration Results":
				InsideData = True
		else:
			if len(Line) != 0 and Line[0].isdigit():
#				Line = Line.replace(".", "")	# for Dutch
#				Line = Line.replace(",", ".")	# for Dutch
				Line = Line.replace(",", "")	# for English
				Time = "{:.2f}".format(round(float(Line.split('\t')[2])
					*RoundTime)/RoundTime)
				Area = float(Line.split('\t')[3])
				if Area >= MinArea and float(Time) >= MinTime:
					AreaData = AddData(Index, Time, AreaData, Area)
					Height = float(Line.split('\t')[4])
					HeightData = AddData(Index, Time,
						HeightData, Height)
					RelArea = float(Line.split('\t')[5])
					RelAreaData = AddData(Index, Time,
						RelAreaData, RelArea)			
	return(SampleList, AreaData, HeightData, RelAreaData, PeakTypeData)

# Combine the data from all files
def GetData(FileList, MinArea, MinTime, RoundTime):
	SampleList = []
	AreaData = {}
	HeightData = {}
	RelAreaData = {}
	PeakTypeData = {}
	Index = 0
	for FileName in FileList:
		(SampleList, AreaData, HeightData, RelAreaData,
			PeakTypeData) = ImportFiles(FileName, MinArea, MinTime,
			RoundTime, Index, SampleList, AreaData, HeightData,
			RelAreaData, PeakTypeData)
		Index += 1
	return(SampleList, AreaData, HeightData, RelAreaData,
		PeakTypeData)

# Export the data to files
def ExportData(SampleList, InputData, Label):
	OutputPath, Folder = os.path.split(InputPath)
	OutputPath = "../" + OutputPath + "_"+ Label + ".txt"
	OutputFile = open(OutputPath, "w")
	OutputFile.write("Samples\t")
	OutputFile.write("\t".join(SampleList))
	for Unit in sorted(InputData.keys(), key=lambda x:float(x)):
		OutputFile.write("\n%s\t" % Unit)
		OutputFile.write("\t".join(map(str,InputData[Unit])))
	print("The %s file has been created" % Label)

#####################################################################
# SCRIPT
#####################################################################

# Import files
DirectoryName, ScriptName = os.path.split(os.path.abspath(__file__))
FilesCorrect = "n"
while FilesCorrect == "n":
	InputPath = GetFolderName(DirectoryName)
	FilesCorrect, FileList = GetFileList(InputPath)
os.chdir(os.path.abspath(InputPath))


MinArea, MinTime, RoundTime = GetValues()
(SampleList, AreaData, HeightData, RelAreaData, PeakTypeData,
	) = GetData(FileList, MinArea, MinTime, RoundTime)


# Export files
ExportData(SampleList, AreaData, "Area")
ExportData(SampleList, HeightData, "Height")
ExportData(SampleList, RelAreaData, "RelativeArea")

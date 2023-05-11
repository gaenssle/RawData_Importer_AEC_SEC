#!/usr/bin/python
# The script has been written in Python 3.5
# Script written by ALO Gaenssle, August 2019

import os

#####################################################################
# FUNCTIONS
#####################################################################
# Print Header
def PrintHeader():
	print("\n","-"*75,"\n","-"*75,"\n")
	print("\tSEC DATA IMPORTER \t\tby A.L.O. Gaenssle, 2019")
	print("\n","-"*75,"\n","-"*75)

# Get name of folder that contains the files to be imported
def GetFolderName(DirectoryName):
	InputPath = input("\nEnter the folder name containing "
		"the files to be imported"
		"\n\nYour current directory is:\n%s"
		"\n\n- If it is a subfolder of the above enter: e.g. FOLDER"
		"\n- Otherwise enter full path: e.g. X:\Experiments\FOLDER\n"
		% DirectoryName)
	while os.path.exists(os.path.abspath(InputPath)) == False:
		InputPath = InputPath.replace("/", "\\")
		if os.path.exists(os.path.abspath(InputPath)):
			break
		InputPath = InputPath.replace("\\", "/")
		if os.path.exists(os.path.abspath(InputPath)):
			break
		InputPath = input("\nThis folder does not exist!"
			"\nPlease enter a correct name"
			"\n(Check the file path by right clicking on "
			"the folder and selecting 'Properties')"
			"\n(Use arrows on keyboard for faster correction)\n")
	return (InputPath)

# Get the names of the files in the folder
def GetFileList(InputPath):
	FileList = []
	for FileName in sorted(os.listdir(os.path.abspath(InputPath))):
		if  FileName.endswith(".txt") or FileName.endswith(".TXT") \
			and not FileName in FileList:
			FileList.append(FileName)
	FileList.sort()
	for FileName in FileList:
		print(FileName)
	FilesCorrect = input("\nAre these files correct?\n"
		"(y=yes, n=no)\n")
	while FilesCorrect not in ("y", "n"):
			FilesCorrect = input("\nPlease enter 'y' or 'n'!\n")
	return(FilesCorrect, FileList)

# Add 0 to Sample IDs under 10
def RenameFileNames(InputPath, FileList):
	for File in range(len(FileList)):
		if len(FileList[File].split("_",1)[0]) == 1:
			os.rename(FileList[File],  "0" + FileList[File])
			FileList[File] = "0" + FileList[File]
	FileList.sort()
	return(FileList)

# Split file into the needed sections
def SplitFile(FileName):
	InsideHeader = True
	InsideRawData = False
	InsideElution = False
	Part_Header = []
	Part_RawData = []
	Part_ElutionData = []
	with open(FileName, 'r', encoding='cp1252') as File:
		for Line in File:
			if InsideHeader == True:
				Part_Header.append(Line.rstrip())
				if Line.startswith("Calibration Coefficients:"):
					InsideHeader = False
			elif InsideRawData == True:
				Part_RawData.append(Line.rstrip())
				if Line.startswith("RAWstop"):
					InsideRawData = False
			elif InsideElution == True:
				Part_ElutionData.append(Line.rstrip())
				if Line.startswith("ELUstop"):
					InsideElution = False
					break
			elif Line.startswith("RAWstart"):
				InsideRawData = True
			elif Line.startswith("ELUstart"):
				InsideElution = True
	return(Part_Header, Part_RawData, Part_ElutionData)

# Extracts information from the calibration and peak analysis
def ExtractInformation(FilePart, Information, HeaderTuple, SampleList):
	for Line in FilePart:
		if Line.startswith("Sample"):
			Line = Line.split('Vial')[1]
			Line = Line.rsplit('-',1)[0]
			Line = Line.strip()
			Sample = Line.split(" ",1)[1]
			SampleList.append(Sample)
		elif Line.startswith(HeaderTuple):
			Line = Line.replace(' ','')
			Key = Line.split(':')[0]
			Value = Line.split('\t')[1]
			if Key in Information:
				Information[Key].append(Value)
			else:
				Information[Key] = [Value]
	return(Information, SampleList)

# Extracts the raw signal data and appends it to the joined data
def ExtractData(FilePart, Index, Data, Type="RawData"):
	if Type == "RawData":
		Column = 1
	else:
		Column = 2
	for Line in FilePart:
		if len(Line) != 0 and Line[1].isdigit():
			Line = Line.replace(' ','')
			Volume = "{:.3f}".format(round(float(Line.split('\t')[0])*60)/60)
			Signal = float(Line.split('\t')[Column])
			if Volume in Data:
				if len(Data[Volume]) <= Index:
					SignalList = ([""]*(Index-len(Data[Volume]))
						+ [Signal])
					Data[Volume].extend(SignalList)
			else:
				SignalList = [""]*Index + [Signal]
				Data.update({Volume:SignalList})
	return(Data)

# Export the data to files
def ExportData(SampleList, InputData, Label):
	OutputPath, Folder = os.path.split(InputPath)
	OutputPath = "../" + OutputPath + "_"+ Label + ".txt"
	OutputFile = open(OutputPath, "w")
	OutputFile.write("Volume\t")
	OutputFile.write("\t".join(SampleList))
	if Label == "Information":
		for Unit in sorted(InputData.keys()):
			OutputFile.write("\n%s\t" % Unit)
			OutputFile.write("\t".join(map(str,InputData[Unit])))
	else:
		for Unit in sorted(InputData.keys(), key=lambda x:float(x)):
			OutputFile.write("\n%s\t" % Unit)
			OutputFile.write("\t".join(map(str,InputData[Unit])))
	print("The %s file has been created" % Label)

#####################################################################
# SCRIPT
#####################################################################

HeaderTuple = ("Internal Standard Calibration",
	"Internal Standard Acquisition", "Mn", "Mw", "Mz", "Mp")

# Import files
DirectoryName, ScriptName = os.path.split(os.path.abspath(__file__))
PrintHeader()
FilesCorrect = "n"
while FilesCorrect == "n":
	InputPath = GetFolderName(DirectoryName)
	FilesCorrect, FileList = GetFileList(InputPath)
os.chdir(os.path.abspath(InputPath))
FileList = RenameFileNames(InputPath, FileList)


# Combine the data from all files
SampleList = []
Information = {}
RawData = {}
ElutionData = {}
for Index in range(len(FileList)):
	Part_Header, Part_RawData, Part_ElutionData = SplitFile(FileList[Index])
	Information, SampleList = ExtractInformation(Part_Header, Information, HeaderTuple, SampleList)
	RawData = ExtractData(Part_RawData, Index, RawData)
	ElutionData = ExtractData(Part_ElutionData, Index, ElutionData, Type="ElutionData")

# Export files
ExportData(SampleList, Information, "Information")
ExportData(SampleList, RawData, "RawData")
ExportData(SampleList, ElutionData, "ElutionData")

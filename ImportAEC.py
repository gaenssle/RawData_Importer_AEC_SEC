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
	print("\tAEC DATA IMPORTER \t\tby A.L.O. Gaenssle, 2019")
	print("\n","-"*75,"\n","-"*75)
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
		InputPath = input("\nFolder %s does not exist!"
			"\nPlease enter a correct name"
			"\n(Check the file path by right clicking on "
			"the folder and selecting 'Properties')"
			"\n(Use arrows on keyboard for faster correction)\n" %InputPath)
	return (InputPath)

# Get the names of the files in the folder
def GetFileList(InputPath):
	FileList = []
	for FileName in os.listdir(os.path.abspath(InputPath)):
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

# Sub-function of GetData
# Import the data from each file
def ImportFiles(FileName, SampleList, Index, RawData):
	InsideRawData = False
	for Line in open(FileName, 'r'):
		Line= Line.rstrip()
		if InsideRawData == False:
			if Line.startswith("Injection\t"):
				Line = Line.split('\t')[1]
				SampleList.append(Line)
			elif Line == "Chromatogram Data:":
				InsideRawData = True
		else:
			if len(Line) != 0 and Line[0].isdigit():
#				Line = Line.replace(".", "") 	# for Dutch
#				Line = Line.replace(",", ".")	# for Dutch
				Line = Line.replace(",", "")	# for English
				Time = "{:.3f}".format(round(float(
					Line.split('\t')[0])*120)/120)
				Signal = float(Line.split('\t')[2])
				if Time in RawData:
					if len(RawData[Time]) <= Index:
						SignalList = ([""]*(Index-len(RawData[Time]))
							+ [Signal])
						RawData[Time].extend(SignalList)
				else:
					SignalList = [""]*Index + [Signal]
					RawData.update({Time:SignalList})
	return(SampleList, RawData)

# Combine the data from all files
def GetData(FileList):
	SampleList = []
	RawData = {}
	Index = 0
	for FileName in FileList:
		(SampleList, RawData) = ImportFiles(FileName, SampleList,
			Index, RawData)
		Index += 1
	return(SampleList, RawData)

# Export the data to files
def ExportData(SampleList, InputData, InputPath):
	OutputPath, Folder = os.path.split(InputPath)
	OutputPath = "../" + OutputPath + "_RawData.txt"
	OutputFile = open(OutputPath, "w")
	OutputFile.write("Samples\t")
	OutputFile.write("\t".join(SampleList))
	for Unit in sorted(InputData.keys(), key=lambda x:float(x)):
		OutputFile.write("\n%s\t" % Unit)
		OutputFile.write("\t".join(map(str,InputData[Unit])))
	print("The raw data file has been created")

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
SampleList, RawData = GetData(FileList)

# Export files
ExportData(SampleList, RawData, InputPath)

#!/usr/bin/python
# The script has been written in Python 3.5
# Script written by ALO Gaenssle, August 2019

import os

#####################################################################
# FUNCTIONS
#####################################################################
# Print Header
def PrintHeader(DirectoryName):
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


# Sub-function of GetData
# Import the data from each file
def ImportFiles(FileName, SampleList, Index, Information, HeaderTuple, RawData, ElutionData):
	Header = True
	InsideRawData = False
	InsideElution = False
	with open(FileName, 'r', encoding='cp1252') as File:
		for Line in File:
			Line= Line.rstrip()
			if Header == True:
				# Import information
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
					Information[Key].append(Value)
				elif Line.startswith("w%"):
					Header = False
			elif Line.startswith("RAWstart"):
				InsideRawData = True
			elif InsideRawData == True:
				# Import RawData
				if len(Line) != 0 and Line[1].isdigit():
					Line = Line.replace(' ','')
					Time = "{:.3f}".format(float(Line.split('\t')[0]))
					Signal = float(Line.split('\t')[1])
					if Time in RawData:
						RawData[Time].append(Signal)
					else:
						# SignalList = [""]*Index + [Signal]
						RawData.update({Time:[Signa]})
				elif Line.startswith("RAWstop"):
					InsideRawData = False
			elif Line.startswith("ELUstart"):
				InsideElution = True
			elif InsideElution == True:
				# Import ElutionData
				if len(Line) != 0 and Line[1].isdigit():
					Line = Line.replace(' ','')
					Volume = "{:.3f}".format(round(float(Line.split('\t')[0])*60)/60)
					Signal = float(Line.split('\t')[2])
					if Volume in ElutionData:
						if len(ElutionData[Volume]) <= Index:
							SignalList = ([""]*(Index-len(ElutionData[Volume]))
								+ [Signal])
							ElutionData[Volume].extend(SignalList)
					else:
						SignalList = [""]*Index + [Signal]
						ElutionData.update({Volume:SignalList})
				elif Line.startswith("ELUstop"):
					InsideElution = False
					break
	return(SampleList, Information, RawData, ElutionData)

# Combine the data from all files
def GetData(FileList):
	SampleList = []
	Information = {"InternalStandardCalibration":[],
	"InternalStandardAcquisition":[],
	"Mn":[], "Mw":[], "Mz":[], "Mp":[]}
	HeaderTuple = ("Internal Standard Calibration",
		"Internal Standard Acquisition", "Mn", "Mw", "Mz", "Mp")
	RawData = {}
	ElutionData = {}
	Index = 0
	for FileName in FileList:
		(SampleList, Information, RawData,
			ElutionData) = ImportFiles(FileName, SampleList, Index,
			Information, HeaderTuple, RawData, ElutionData)
		Index += 1
	return(SampleList, Information, RawData, ElutionData)

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
			print("\t".join(map(str,InputData[Unit])))
	print("The %s file has been created" % Label)

#####################################################################
# SCRIPT
#####################################################################

# Import files
DirectoryName, ScriptName = os.path.split(os.path.abspath(__file__))
PrintHeader(DirectoryName)
FilesCorrect = "n"
while FilesCorrect == "n":
	InputPath = GetFolderName(DirectoryName)
	FilesCorrect, FileList = GetFileList(InputPath)
os.chdir(os.path.abspath(InputPath))
FileList = RenameFileNames(InputPath, FileList)
SampleList, Information, RawData, ElutionData = GetData(FileList)

# Export files
# ExportData(SampleList, Information, "Information")
ExportData(SampleList, RawData, "RawData")
# ExportData(SampleList, ElutionData, "ElutionData")

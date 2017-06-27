from __future__ import print_function
import os
import serpent

# TODO: only regenerate this file if one of the source files has changed since this file was created

def generateExternForFile(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    signatureOutput = serpent.mk_signature(filePath)
    signature = signatureOutput.split(': ', 1)[1]
    signature = signature.replace(':,', ':int256,').replace(':]', ':int256]')
    externLine = 'extern ' + name + 'Extern: ' + signature
    return(externLine)

def getAllFilesInDirectories(sourceDirectories):
    allFilePaths = []
    for directory in sourceDirectories:
        files = os.listdir(directory)
        for file in files:
            allFilePaths.append(directory + file)
    return(allFilePaths)

externLines = []
for filePath in (getAllFilesInDirectories(['./factories/', './libraries/', './reporting/', './trading/', './extensions/']) + ['./controller.se', './mutex.se']):
    externLines.append(generateExternForFile(filePath))

with open('./macros/externs.sem', 'w') as externsFile:
    for externLine in externLines:
        print(externLine, file=externsFile)

from __future__ import print_function
from os import path, listdir
from serpent import mk_signature

# TODO: only regenerate this file if one of the source files has changed since this file was created

def generateExternForFile(filePath):
    name = path.splitext(path.basename(filePath))[0]
    signatureOutput = mk_signature(filePath)
    signature = signatureOutput.split(': ', 1)[1]
    signature = signature.replace(':,', ':int256,').replace(':]', ':int256]')
    externLine = 'extern ' + name + 'Extern: ' + signature
    return(externLine)

def getAllFilesInDirectories(sourceDirectories):
    allFilePaths = []
    for directory in sourceDirectories:
        files = listdir(directory)
        for filename in files:
            if path.splitext(filename)[1] != '.se': continue
            allFilePaths.append(directory + filename)
    return(allFilePaths)

externLines = []
for filePath in (getAllFilesInDirectories(['./factories/', './libraries/', './reporting/', './trading/', './extensions/']) + ['./mutex.se']):
    externLines.append(generateExternForFile(filePath))

with open('./macros/externs.sem', 'w') as externsFile:
    for externLine in externLines:
        print(externLine, file=externsFile)

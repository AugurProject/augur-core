#----------------------------------------------------------------
#Imports libraries
#----------------------------------------------------------------

import glob
import os
import sys

#----------------------------------------------------------------
#Gathers from user list of folders to concatenate .se files from and options
#----------------------------------------------------------------

folderpath = []
foldercount = 0
i = 0
while(i < len(sys.argv)):
    folderpath.append(str(sys.argv[i]))
    i += 1
    foldercount += 1
morefolders = 0
foldercount -= 1
if(os.path.isfile(str(sys.argv[i-1]) + '/output.se')):
    os.remove(str(sys.argv[i-1]) + '/output.se')
removeintro = 1

	
#----------------------------------------------------------------
#Read files change the content in memory and save the result as a new file
#----------------------------------------------------------------	
	
maindataline = []
index = 0
while index < foldercount:												#loops all selected folders
    for filename in glob.glob(os.path.join(folderpath[index], '*.se')):		#loops all files in current folder
        rawdata = ""    #clears rawdata string
        print filename
        with open(filename,"r") as rawdata:
            rawdataline = []                                            #List of lines in source file
            for line in rawdata: 										#loops all lines in current file
                rawdataline.append(line)
        if removeintro:
            preinstruction = 1
            while preinstruction:                                        #removees starting lines that are comments or empty
                if rawdataline[0][0] == '\n' or rawdataline[0][0] == '#':
                    rawdataline.pop(0)
                else:
                    preinstruction = 0
        removingimports = 1
        while removingimports:
            if rawdataline[0][0] == '\n' or rawdataline[0][:6] == "import":
                rawdataline.pop(0)
            else:
                removingimports = 0
        indexline = 0
        while indexline < len(rawdataline):                                      #loop every line in rawdataline
            indexchar = 0
            while indexchar < len(rawdataline[indexline]):                       #loop every character in current line
                capsfound = 0
                if rawdataline[indexline][indexchar] == ".":
                    indexcap = 0    #number of capital letters found so far
                    while rawdataline[indexline][(indexchar-indexcap-1)].isupper():
                        rawdataline[indexline] = rawdataline[indexline][:indexchar-indexcap-1] + rawdataline[indexline][indexchar-indexcap:]  #remove prior letter
                        indexcap += 1
                        capsfound = 1
                if capsfound:                                                #adds self before the period
                    indexchar = indexchar - indexcap                          #adjusts indexchar to make up for characters being removed
                    indexcap = 0
                    capsfound = 0
                    rawdataline[indexline] = rawdataline[indexline][:(indexchar)] + "self" + rawdataline[indexline][(indexchar):]
                indexchar += 1
                #end of character loop
            maindataline.append(rawdataline[indexline])                          #adds the modified line to the main data compilation
            indexline += 1
            #end of line loop
        maindataline.append('\n')
        #end of file loop
    index += 1
    #end of folder loop
savepath = folderpath[foldercount] + "/output.se"
file = open(savepath, "w")
file.seek(0, 2)
line = file.writelines(maindataline)
file.close()

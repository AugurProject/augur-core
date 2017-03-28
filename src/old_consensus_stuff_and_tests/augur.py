from __future__ import division
import math
import random

def initiate(numEvents, numReporters):
    # need a bunch of random events
    # w/ random volumes
    totalVol = 0
    numberReportEstimate = 0
    listVol = []
    maxVol = 1000000
    for x in range(0, numEvents):
        curVol = random.randint(1, maxVol)
        listVol.append(curVol)
        totalVol += curVol
        maxVol -= int(curVol/10)
    for x in range(0, numEvents):
        z = listVol[x] / totalVol
        numberReportEstimate += 40
            #or num reporters - gives you directly % of reporters reporting on an event
            # do a minimum to max function, min 30 then multiply by volume from 0-1 up to max
            #30*(-(267 x^2)/2+(533 x)/2+1) with x as fraction of volume

            # need a bunch of reporters w/ random rep #s
    reporterList = []
    eventsExpected = []
    totalRep = 0
    eventsActually = []
    maxRep = 11000000*10**18
    for n in range(0, numReporters):
        rep = random.randint(0, maxRep)
        reporterList.append(rep)
        totalRep += rep
        maxRep -= int(rep/10)
    lowestVolNum = 0
    reportsOnLowest = 0
    lowestVolAmt = 11000000*TWO
    for z in range(0, numEvents):
        if(listVol[z]<lowestVolAmt):
            lowestVolNum = z
    for n in range(0, numReporters):
        # need to calc. num events per reporter expected
        eventsExpected.append(numberReportEstimate*((reporterList[n]/totalRep)**1.2+.001))
        eventsActuallyReporter = []
        # maybe increase 50 to 60 or do 1.1 instead of 1.2
        for z in range(0, numEvents):
            # need to use a rng to see how many really reported on
            volFraction = listVol[z]/totalVol
            repConstant = (reporterList[n]/totalRep)**1.2+.001
            reportingThreshold = (40*(-(267*volFraction**2)/2+(533*volFraction)/2+1)*repConstant)*2**256
            #reportingThreshold = (math.sqrt(listVol[z]/totalVol)*50*reporterList[n]/totalRep)*2**256
            if(random.randint(0, 2**256)<reportingThreshold):
                eventsActuallyReporter.append(1)
                if(z==lowestVolNum):
                    reportsOnLowest += 1
        eventsActually.append(len(eventsActuallyReporter))

    difference = []
    last = 0
    lastReporter = 0
    for y in range(0, numReporters):
        if(eventsExpected[y]>numEvents):
            difference.append(numEvents - eventsActually[y])
        else:
            difference.append(eventsExpected[y] - eventsActually[y])
        if(difference[y]>last):
            last = difference[y]
            lastReporter = y
    # last is worst case difference between number of events selected to report on and what we expect
    avg = 0
    for x in range(0, numReporters):
        avg += difference[x]
    avg = avg/numReporters
    #    return(avg)
    lastExpectation = 100
    reporterLast = 0
    for z in range(0, numReporters):
        if(eventsExpected[z]>numEvents):
            eventsExpected[z] = numEvents
        if(eventsActually[z]/eventsExpected[z] < .55):
            return(1)
            #if(eventsActually[z]/eventsExpected[z]<lastExpectation):
             #   lastExpectation = eventsActually[z]/eventsExpected[z]
              #  reporterLast = z
    return(0)
    # events reported on by 3rd reporter, % rep of 3rd reporter, events reported on by last reporter, % rep of last reporter
    #return(reporterList[numReporters-1]/totalRep, eventsActually[numReporters-1], eventsExpected[numReporters-1], eventsActually[numReporters-1]/eventsExpected[numReporters-1], reportsOnLowest)

    def go(numEvents, numReporters):
        for x in range(0,numEvents):
            for y in range(0, numReporters):
                if(self.initiate(x, y)==1):
                    return("damn")
        return(1)
# loop through all and make sure none < .5
# min rep to report
# atk by making a ton of accounts and reporting
# hash precomputing attack
from __future__ import division
import math
import random

def initiate(numEvents, numReporters):
    # need a bunch of random events
    # w/ random volumes
    totalVol = 0
    numberReportEstimate = 0
    listVol = []
    lowestVolNum = 0
    lowestVolAmt = 11000000*TWO
    maxVol = 1000000
    for x in range(0, numEvents):
        curVol = random.randint(1, maxVol)
        listVol.append(curVol)
        totalVol += curVol
        maxVol -= int(curVol/10)
        numberReportEstimate += 40
        if(curVol<lowestVolAmt):
            lowestVolNum = x
            lowestVolAmt = curVol
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
    reportsOnLowest = 0
    reports = 0
    for n in range(0, numReporters):
        # need to calc. num events per reporter expected
        est = numberReportEstimate*((reporterList[n]/totalRep)**1.2+.001)
        repConstant = (reporterList[n]/totalRep)**1.2+.001
        if(est < 30):
            # min. of 30 events no matter how little rep you have
            repConstant = 30/numberReportEstimate
            eventsExpected.append(30)
        else:
            eventsExpected.append(numberReportEstimate*((reporterList[n]/totalRep)**1.2+.001))
        eventsActuallyReported = 0
        # maybe increase 50 to 60 or do 1.1 instead of 1.2
        for z in range(0, numEvents):
            # need to use a rng to see how many really reported on
            volFraction = listVol[z]/totalVol
            reportingThreshold = (40*(-(267*volFraction**2)/2+(533*volFraction)/2+1)*repConstant)*2**256
            #reportingThreshold = (math.sqrt(listVol[z]/totalVol)*50*reporterList[n]/totalRep)*2**256
            if(random.randint(0, 2**256)<reportingThreshold):
                eventsActuallyReported += 1
                reports += 1
                if(z==lowestVolNum):
                    reportsOnLowest += 1
        eventsActually.append(eventsActuallyReported)
    reports = reports/numEvents

    #difference = []
    #last = 0n
    #lastReporter = 0
    #for y in range(0, numReporters):
    #    if(eventsExpected[y]>numEvents):
    #        difference.append(numEvents - eventsActually[y])
    #    else:
    #        difference.append(eventsExpected[y] - eventsActually[y])
    #    if(difference[y]>last):
    #        last = difference[y]
    #        lastReporter = y
    # last is worst case difference between number of events selected to report on and what we expect
    #avg = 0
    #for x in range(0, numReporters):
    #    avg += difference[x]
    #avg = avg/numReporters
    #    return(avg)
    #lastExpectation = 100
    #reporterLast = 0
    for z in range(0, numReporters):
        if(eventsExpected[z]>numEvents):
            eventsExpected[z] = numEvents
        if(eventsActually[z]/eventsExpected[z] < .50):
            return(reporterList[z]/totalRep, eventsExpected[z], eventsActually[z], reportsOnLowest)
            #if(eventsActually[z]/eventsExpected[z]<lastExpectation):
             #   lastExpectation = eventsActually[z]/eventsExpected[z]
              #  reporterLast = z
    #return(reportsOnLowest, reports)
    return(0)
    # events reported on by 3rd reporter, % rep of 3rd reporter, events reported on by last reporter, % rep of last reporter
    #return(reporterList[numReporters-1]/totalRep, eventsActually[numReporters-1], eventsExpected[numReporters-1], eventsActually[numReporters-1]/eventsExpected[numReporters-1], reportsOnLowest)

def go():
    for x in range(1,numEvents):
        for y in range(1, numReporters):
            n = initiate(x, y)
            if(n!=0):
                return("damn", n, x, y)
    return(1)

if __name__ == '__main__':
    print go()
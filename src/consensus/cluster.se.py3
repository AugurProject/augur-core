data best = -1
data bestDist = 2^255
# list of clusterIDs
data bestClusters[]

import expiringEvents as EXPEVENTS
import reporting as REPORTING

# vect should either be a list of ballots or a list of reporters
# meanVec is numEvents long
# vec is numEvents*numReporters long
# could get rep vector from our list of reporters
# or could just use reporterIndex vec to get both rep & ballots
data clusternodes[](vec[], numReporters, meanVec[], repInCluster, repVector, reporterIndexVec, distance)

def cluster():

def L2dist(x:arr, y:arr, numEvents):
    i = 0
    distSquare = 0
    while i < numEvents:
        distSquare += (x[i] - y[i])^2
        i += 1
    return(self.sqrt(distSquare))

def sqrt(n):
    approx = n/2
    better = (approx + n/approx)/2
    i = 0
    while i < 11:
        approx = better
        better = (approx + n/approx)/2
        i += 1
    return approx

def newMean(cluster, numEvents, branch, reportingPeriod):
	numReporters = self.clusternodes[cluster].numReporters
	weighted = array(numReporters)
	i = 0
	while i < numReporters:
		weighted[i] = array(numReporters)
		reporterID = REPORTING.getReporterID(branch, reporterIndexVec[i]):
		weighted[i] = EXPEVENTS.getReporterBallot(branch, reportingPeriod, reporterID, outitems=numEvents)
		e = 0
		while e < numEvents:
			weighted[i][e] *= REPORTING.getRepBalance(branch, reporterID)
			e += 1
		i += 1
	mean = array(numEvents)
	i = 0
	totalRep = self.clusternodes[cluster].repInCluster
	while i < numEvents:
		r = 0
		while r < numReporters:
			mean[i] += weighted[r][i]
			r += 1
		mean[i] /= totalRep
		i += 1
	return(mean: arr)
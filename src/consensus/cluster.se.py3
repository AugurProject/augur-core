data best = -1
data bestDist = 2^255
# list of clusterIDs
data bestClusters[]
data step

import expiringEvents as EXPEVENTS
import reporting as REPORTING
import clusterhelper as CLUSTER
import fxpFunctions as FXP

# vec should either be a list of ballots or a list of reporters
# meanVec is numEvents long
# vec is numEvents*numReporters long
# could get rep vector from our list of reporters
# or could just use reporterIndex vec to get both rep & ballots

# overwriting of data issues etc
data clusternodes[](meanVec[], numReporters, reporterIndexVec[], repVector[], repInCluster, distance)
data numClusters

def initCluster(branch, votePeriod, numEvents, numReporters):
	threshold = (FXP.fx_log(numEvents*2^64)*2^64/42475197863169474560)*2^64 / 32650737010465906688
	if(threshold==0):
		threshold = 5534023222112865280
	self.best = -1
	self.bestDist = 2**255
	self.numClusters = 0
	self.step = 0
	return(cluster(branch, votePeriod, numEvents, numReporters))

def cluster(branch, votePeriod, numEvents, numReporters):
	currentclustid = -1
	i = 0
	while i < numReporters:
		cmax = -1
		shortestDist = 2**255
		n = 0
		while n < numClusters:
			if(n!=0):
				dist = CLUSTER.L2dist(reportorsomething, self.clusternodes[n].meanVec)
				if dist<shortestDist:
					cmax = n
					shortestDist = dist
			n += 1
		if(cmax!=-1 and shortestDist<threshold):
			self.clusternodes[cmax].reporterIndexVec[self.clusternodes[cmax].numReporters] = i
			self.clusternodes[cmax].repInCluster += getreporterrep
			self.clusternodes[cmax].repVector[self.clusternodes[cmax].numReporters] = getreporterreps
			self.clusternodes[cmax].numReporters += 1
			self.clusternodes[cmax].meanVec[] = array(mean(cmax))
        else:
        	self.clusternodes[self.numClusters].meanVec[] = reporterreport
        	self.clusternodes[self.numClusters].numReporters = 1
        	self.clusternodes[self.numClusters].repInCluster = getreporterrep
        	self.clusternodes[self.numClusters].reporterIndexVec[0] = i
        	self.clusternodes[self.numClusters].repVector[0] = getreporterrep
    #clusters = process(clusters, len(features), times, features, rep, threshold)
    return clusters

# Proportional distance from zero (fixed-point input)
macro normalize($a):
    with $len = len($a):
        with $total = 0:
            with $i = 0:
                while $i < $len:
                    $total += $a[$i]
                    $i += 1
                with $wt = array($len):
                    with $i = 0:
                        while $i < $len:
                            $wt[$i] = $a[$i] * 2^64 / $total
                            $i += 1
                        $wt
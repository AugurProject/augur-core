import expiringEvents as EXPEVENTS
import reporting as REPORTING
import clusterhelper as CLUSTER
import fxpFunctions as FXP

# first call in a consensus cycle is fresh, else 0
def initCluster(branch, votePeriod, numEvents, numReporters, fresh):
	threshold = (FXP.fx_log(numEvents*2^64)*2^64/42475197863169474560)*2^64 / 32650737010465906688
	if(threshold==0):
		threshold = 5534023222112865280
	CLUSTER.setBest(-1)
	CLUSTER.setBestDist(2**255)
	CLUSTER.setNumClusters(0)
	return(CLUSTER.cluster(branch, votePeriod, numEvents, numReporters, fresh))
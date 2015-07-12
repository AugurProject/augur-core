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
    return(CLUSTER.cluster(branch, votePeriod, numEvents, numReporters, fresh, threshold))

def smooth(reputation:arr, num_reports, num_events):
    # Weighted sum of old and new reputation vectors.
    # New: row_reward_weighted
    # Old: reputation
    adjusted_scores = array(num_reports)
    adjusted_scores = CLUSTER.getRepVector(outitems=num_reports)

    reputation = array(num_reports)
    i = 0
    while i < num_reports:
        reporterID = REPORTING.getReporterID(branch, i)
        reputation[i] = REPORTING.getRepBalance(branch, reporterID)
        i += 1

    reputation = normalize(reputation)

    with row_reward_weighted = array(num_reports):
        with i = 0:
            while i < num_reports:
                row_reward_weighted[i] = reputation[i]
                i += 1
        # Overwrite the inital declaration IFF there wasn't perfect consensus.
        if maximum(array_abs(adjusted_scores)) != 1:
            with mean_weight = mean(row_reward_weighted):
                with i = 0:
                    while i < num_reports:
                        row_reward_weighted[i] = adjusted_scores[i] * row_reward_weighted[i] / mean_weight
                        i += 1
            row_reward_weighted = normalize(row_reward_weighted)
        # Freshly-calculated reward (in reputation)
        # (0.2 is the adjustable parameter "alpha", hard-coding it for now)
        with smooth_rep = array(num_reports):
            with i = 0:
                while i < num_reports:
                    smooth_rep[i] = row_reward_weighted[i]*2/10 + reputation[i]*8/10
                    i += 1
            smooth_rep = normalize(smooth_rep)
            with i = 0:
                with totalRep = REPORTING.getTotalRep(branch):
                    while i < num_reports:
                        REPORTING.setRep(branch, i, smooth_rep[i]*totalRep)
            return(smooth_rep, items=num_reports)

# Maximum value of array
macro maximum($a):
    with $max = $a[0]:
        with $i = 1:
            with $len = len($a):
                while $i < $len:
                    if $a[$i] > $max:
                        $max = $a[$i]
                    $i += 1
                $max

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
import expiringEvents as EXPIRING
import reporting as REPORTING
import clustering as CLUSTER
import fxpFunctions as FXP
import outcomes as OUTCOMES
import branches as BRANCHES
import checkQuorum as QUORUM
import events as EVENTS
import cash as CASH
import info as INFO

macro ONE: 2^64
macro BAD: 3 * 2^63
macro BOND: 42 * ONE

def dispatch(branch):
    #if !BRANCHES.getStep(branch) and !QUORUM.checkQuorum(branch):
    #    return(-1)
    with period = BRANCHES.getVotePeriod(branch):
        with num_events = EXPIRING.getNumberEvents(branch, period):
            with num_reports = REPORTING.getNumberReporters(branch):
                with step = BRANCHES.getStep(branch):
                    if step == 4:
                        self.payout(branch, period, num_events, num_reports)
                        BRANCHES.setStep(branch, 0) # reset step
                        BRANCHES.incrementPeriod(branch)
                        return(period + 1)
                    elif step == 0:
                        EXPIRING.setTotalReputation(branch, period, REPORTING.getTotalRep(branch))
                    elif step == 1:
                        x = self.initCluster(branch, period, num_events, num_reports, 1)
                        if(x):
                            # increment 2x if it gets all done in 1st call, else go to step 2
                            BRANCHES.incrementStep(branch)
                    elif step == 2:
                        threshold = (FXP.fx_log(numEvents*2^64)*2^64/42475197863169474560)*2^64 / 32650737010465906688
                        if(threshold==0):
                            threshold = 5534023222112865280
                        # if not done, keep doing step two before incrementing the step
                        if(!CLUSTER.cluster(branch, period, num_events, num_reports, 0, threshold)):
                            return(2)
                    elif step == 3:
                        self.smooth(num_reports, num_events)
                    elif step == 4:
                        OUTCOMES.resolve(branch, period, num_events, num_reports)
                    BRANCHES.incrementStep(branch)
                    return(step + 1)

# first call in a consensus cycle is fresh, else 0
def initCluster(branch, votePeriod, numEvents, numReporters, fresh):
    threshold = (FXP.fx_log(numEvents*2^64)*2^64/42475197863169474560)*2^64 / 32650737010465906688
    if(threshold==0):
        threshold = 5534023222112865280
    CLUSTER.setBest(-1)
    CLUSTER.setBestDist(2**255)
    CLUSTER.setNumClusters(0)
    CLUSTER.setI(0)
    return(CLUSTER.cluster(branch, votePeriod, numEvents, numReporters, fresh, threshold))

def smooth(num_reports, num_events):
    # Weighted sum of old and new reputation vectors.
    # New: row_reward_weighted
    # Old: reputation
    adjusted_scores = array(num_reports)
    adjusted_scores = CLUSTER.getRepVector(num_reports, outitems=num_reports)

    reputation = array(num_reports)
    i = 0
    while i < num_reports:
        reputation[i] = REPORTING.getRepByIndex(branch, i)
        i += 1

    reputation = normalize(reputation)

    with row_reward_weighted = array(num_reports):
        with i = 0:
            while i < num_reports:
                row_reward_weighted[i] = reputation[i]
                i += 1
        # Overwrite the inital declaration IF there wasn't perfect consensus.
        if minimum(adjusted_scores) != 2^64:
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
                with totalRep = EXPIRING.getTotalReputation(branch):
                    while i < num_reports:
                        REPORTING.setRep(branch, i, smooth_rep[i]*totalRep)
            return(1)

def payout(branch, period, num_events, num_reports):
        with outcomes = array(num_events):
            outcomes = slice(EXPIRING.getOutcomesFinal(branch, period, outitems=num_events), items=0, items=num_events)
            # get event ID for each event by taking the x index in the reports arrays
            # - shoving it in reporting.events[] and getting the corresponding ID
            with j = 0:
                while j < num_events:
                    with event = EXPIRING.getEvent(branch, period, j):
                        # then take outcomes_final and set each event outcome
                        # (BAD and BOND macros defined in consensus/constants.se)
                        EVENTS.setOutcome(event, outcomes[j])
                        if outcomes[j] != BAD:
                            # return bond
                            CASH.subtractCash(event, BOND)
                            CASH.addCash(INFO.getCreator(event), BOND)
                        else:
                            # give event bond money to reporters
                            CASH.subtractCash(event, BOND)
                            CASH.addCash(branch, BOND)
                    j += 1
            # - need to loop through rep holders and distribute 50% of branch fees to
            #   reporters' cashcoin addresses
            with totalRep = REPORTING.getTotalRep(branch):
                with i = 0:
                    while i < num_reports:
                        CASH.addCash(REPORTING.getReporterID(branch, i), fixed_multiply(CASH.balance(branch), REPORTING.getRepByIndex(branch, i)*2^64/totalRep))
                        i += 1
                    CASH.subtractCash(branch, CASH.balance(branch))
    return(1)

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

# Minimum value of array
macro minimum($a):
    with $min = $a[0]:
        with $i = 1:
            with $len = len($a):
                while $i < $len:
                    if $a[$i] < $min:
                        $min = $a[$i]
                    $i += 1
                $min
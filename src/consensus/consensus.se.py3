# Use consistent 1 and 2 fixed point numbers as min and max for close market, make market, make event, buy/sell shares, and consensus on binary events - really, just use base 64 fixed point everywhere
# while loops

#separate sets of rep
#After a user has started doing pen calcs but before they've gotten new normalized rep, don't allow sending of rep
#Also don't allow conversion of rep after selection of events for a voting period has started, otherwise you can report on 1-2 but reap rewards as if it's a lot of rep.  So it can't be used until next period (ie there's a holding period)
#Abe limit order writeup

#  only resolve ones that had odds <99% for one of the outcomes.
# We should probably still have an option to pay to resolve in case something somehow goes wrong here (or if not enough reports).  This also doesn't work for scalar markets (although it does for categorical).

# Two initial branches - one only for oracle system no markets
	# - on all branches besides oracle branch, if an event isn’t in a market, it shouldn’t be reported on at all

import expiringEvents as EXPIRING
import reporting as REPORTING
import fxpFunctions as FXP
import events as EVENTS
import makeReports as REPORTS

data proportionCorrect[]
# takes branch, votePeriod
data denominator[][]

# separate voting unethical and event outcome for .5 reports


#1. Record rep at start of report period
#2. Penalize for each event
#	- subtract from 1 and store in another variable if a loss
#	- add to 1 and store in another variable if win rep
#3. Always keep updated the current denominator, so totalRep + delta from 2
	#3a. Make it so a user has to do this for all events they reported on _before_ updating the denominator
#4. Do 2 and 3 for each reporter (note: each reporter needs to do this for all events they reported on, if not get docked)
#5. At the end of some period make so users have to claim rep (win/loss var for a user / (current denominator) * totalRepInPeriod)
#6. If you don't do it for all events, autolose 20% rep (b/c you're trying to cheat)
#7. what if don't claim rep, nothing, it just doesn't formally exist until you claim it or try to send it somewhere (upon which it claims your old rep)
# make sure user has always done this up to current period before doing current period
def penalizeWrong(branch, period, event):
	if(notDoneForEvent && periodOver && reported):
		p = self.getProportionCorrect(event)
		outcome = EVENTS.getOutcome(event)
		reportValue = REPORTS.getReport(branch,period,event)
		oldRep = REPORTS.getBeforeRep(branch, period)
		# wrong
		if(reportValue > outcome+.01 or reportValue < outcome-.01):
			if(scalar or categorical):
				p = -(abs(reportValue - EVENTS.getMedian(event))/2) + 1
			newRep = oldRep*(2*p -1)
		# right
		else:
			if(scalar or categorical):
				p = -(abs(reportValue - EVENTS.getMedian(event))/2) + 1
			newRep = oldRep*(2*(1-p)**2 / p + 1)
		smoothedRep = oldRep*.8 + newRep*.2
		REPORTS.setAfterRep(branch, period, oldRep + (smoothedRep - oldRep))
		if(doneForAllEventsUserReportedOn):
			totalRepReported = EXPIRING.getTotalRepReported(branch, votePeriod)
			self.denominator[branch][period] = totalRepReported + (smoothedRep - oldRep)
		return(1)
	else:
		return(0)

macro abs($a):
	if($a<0):
		$a = -$a
	$a

def proportionCorrect(event):
	if(notDoneForEvent && periodOver && reported):
		# p is proportion of correct responses
		p = 0
		# real answer is outcome
		outcome = EVENTS.getOutcome(event)
		if(outcome!=0):
			# binary
			if(EVENTS.getNumOutcomes(event)==2 and 2**64*EVENTS.getMaxValue(event)==2**65):
				avgOutcome = EVENTS.getUncaughtOutcome(event)
				# say we have outcome of 0, avg is .4, what is p?
				# p is .6 or 60%
				if(outcome == 2**64):
					p = 1 - avgOutcome
				# say we have outcome of 1, avg is .8, what is p (proportion correct)?
					# p is .8 or 80%
				if(outcome == 2 * 2**64):
					p = avgOutcome
				# say we have outcome of .5, avg is .55, what is p?
				if(outcome == 3 * 2**63):
		return(p)
	else:
		return(0)

def getProportionCorrect(event):
	return(self.proportionCorrect[event])

# At the end of some period make so users have to claim rep (win/loss var for a user / (current denominator) * totalRepInPeriod)
# what is window to do this?
def collectRegularRep(branch, votePeriod):
	if(periodOver && reportedEnough && claimedProportionCorrectEnough && hasDoneRRForLazyEventsAndWrongAnsForPastOrGottenPenaltyBelow && hasn'tDoneThisAlready):
		totalRepReported = EXPIRING.getTotalRepReported(branch, votePeriod)
		# denominator (so it is normalized rep)
		denominator = REPORTS.getAfterRep(branch, period)
		# new rep pre normalization
		newRep = REPORTS.getAfterRep(branch, period)
		# after normalization
		newRep =  newRep * 2**64 / denominator * totalRepReported / 2**64
		REPORTING.setRep(branch, REPORTING.repIDToIndex(branch, tx.origin), newRep)
		return(1)
	else:
		return(0)


# rep claiming similar to fee claiming
# person didn't report enough
def collectPenaltyRep(branch, votePeriod):
	# if reported not enough for this period, don't allow collection
	numEvents = REPORTS.getNumEventsToReportOn(branch, votePeriod)
	if(numEvents < 30*2**64):
        numEvents = 30*2**64
    if(numEvents/(2*2**64) > REPORTS.getNumReportsActual(branch, votePeriod)):
    	return(-1)
    if(hasntDoneRRForLazyEventsAndWrongAnsForPast+CurrentPeriods):
        doIt()
        self.RRDone = true
    if(oldPeriodsTooLateToPenalize && userDidntPenalizeForAllInOldPeriods):
    	# dock rep by 20% for each period they didn't
    	smoothedRep = oldRep*.8
    	# and send it to branch for penalty rep collection
    lastPeriod = BRANCHES.getVotePeriod(branch)-1
    repReported = EXPEVENTS.getTotalRepReported(branch, lastPeriod)
    if(penaltyNotAlreadyCollected && periodOver && hasReported && collectedRepForPeriod)
    	rep = fixed_multiply(REPORTING.getInitialRep(branch, lastPeriod), REPORTING.getReputation(msg.sender)*2**64/repReported)
    	REPORTING.addRep(branch, REPORTING.repIDToIndex(branch, tx.origin), rep)
		REPORTING.subtractRep(branch, REPORTING.repIDToIndex(branch, branch), rep)
	return(1)

#Q: Can we do lazy eval claiming of trading fees?
#A: Yes:
#      if(addrWasInThisConsensusPeriod):
#          send them cash of amount equal to fees from that period * rep owned by addr in that period / total #rep in that period
# payout function (lazily evaluate it)
def collectFees(branch):
	# if reported not enough for this period, don't allow collection
	numEvents = REPORTS.getNumEventsToReportOn(branch, votePeriod)
	if(numEvents < 30*2**64):
        numEvents = 30*2**64
    if(numEvents/(2*2**64) > REPORTS.getNumReportsActual(branch, votePeriod)):
    	return(-1)
	# - need to loop through rep holders and distribute 50% of branch fees to
	# except instead, do it on a per report basis
    # reporters' cashcoin addresses
    if(hasntDoneRRForLazyEventsAndWrongAnsForPast+CurrentPeriods):
        doIt()
        self.RRDone = true
    lastPeriod = BRANCHES.getVotePeriod(branch)-1
    repReported = EXPEVENTS.getTotalRepReported(branch, lastPeriod)
    if(feesNotAlreadyCollected && periodOver && hasReported)
		cash = fixed_multiply(BRANCHES.getInitialBalance(branch, lastPeriod), REPORTING.getReputation(msg.sender)*2^64/repReported)
		CASH.addCash(msg.sender, cash)
		CASH.subtractCash(branch, cash)
	return(1)

# concept of event finality and time periods
# need a way to penalize by round 2 as well
# https://www.reddit.com/r/Augur/comments/3mco9m/dynamic_vs_fixed_bond_amount_for_readjudication/
def roundTwoBond(event):
	bond == 100 rep
	# penalize wrong same as above
	# penalize not enough separately

	# 2 week voting period

	if(overruled && votedOnAgain):
		#a) return the bond
		#b) reward the bonded challenger with whatever rep would normally be taken from the liars up to 2x the bond, then beyond that the people who originally reported whatever the actual truth was would get the rest.
		return(2*bond)
	elif(votedOnAgain):
		lose bond
	# set round two to true


#Essentially, we could allow anyone to pay some amount significantly greater than the bond amount to force a branching event, splitting rep into two classes.*  In one class the reported outcome for whatever event was the cause of dispute is said to be right, and rep would be redistributed accordingly.  In the other class/branch, the other outcome would be considered right and rep would be redistributed accordingly.  Whichever outcome was truly the correct one would determine which branch had rep that actually held value.  This would be akin to a Bitcoin hard fork scenario.  The winning fork, of course, would be the one with the most voluminous markets.  Market makers should then be able to move their market to whichever fork they want, if they fail to act, it'd go to the most voluminous fork by default after a couple weeks.
# Errors:
	# -1: round two hasn't happened yet
def fork(event):
	if(!EVENTS.getRoundTwo(event)):
		return(-1)
	# branch 1
		# lose bond
		# results same as roundtwobond
	# branch 2
		# results opposite as roundtwobond
		#a) return the bond
		#b) reward the bonded challenger with whatever rep would normally be taken from the liars up to 2x the bond, then beyond that the people who originally reported whatever the actual truth was would get the rest.
		#Additionally, the rewards for all other answerers are made more extreme: rep redistribution constant used for smoothing is .40 instead of .2

def incrementPeriodAfterReporting():
	# do this after reporting is finished
	if(reportingPeriodOver/finished):
		BRANCHES.incrementPeriod(branch)
		return(1)
	else:
		return(0)

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

# Sum elements of array
macro sum($a):
    with $len = len($a):
        with $total = 0:
            with $i = 0:
                while $i < $len:
                    $total += $a[$i]
                    $i += 1
                $total
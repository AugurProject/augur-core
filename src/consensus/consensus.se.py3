import expiringEvents as EXPIRING
import reporting as REPORTING
import fxpFunctions as FXP
import events as EVENTS
import makeReports as REPORTS
import branches as BRANCHES
import sendReputation as SENDREP

data proportionCorrect[]
# takes branch, votePeriod
data denominator[][]

data roundTwo[](roundTwo, originalVotePeriod, originalOutcome)

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
# Errors:
  # -1: pushed back event already resolved, so can't redistribute rep based off of its original expected expiration period
def penalizeWrong(branch, period, event):
  if(EVENTS.getOriginalExpiration(event)!=EVENTS.getExpiration(event)):
    if(period==EVENTS.getOriginalExpiration(event)/BRANCHES.getPeriodLength(branch)):
      return(-1)

	if(notDoneForEvent && periodOver && reported && eventResolvedInCloseMarket && eventInPeriod):
		p = self.getProportionCorrect(event)
		outcome = EVENTS.getOutcome(event)
		reportValue = REPORTS.getReport(branch,period,event)
		oldRep = REPORTS.getBeforeRep(branch, period)
		# wrong
		if(reportValue > outcome+.01 or reportValue < outcome-.01):
			if(scalar or categorical):
        # should be outcome since median is the same
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

  if(rejected && rejectedPeriod periodOver && reported && eventResolvedInCloseMarket && notDoneForRejectedEvent):
    outcome = 2**63
    median = 2**63
		p = self.getProportionCorrect(event, rejected)
		reportValue = REPORTS.getReport(branch,period,event)
		oldRep = REPORTS.getBeforeRep(branch, period)
		# wrong
		if(reportValue > outcome+.01 or reportValue < outcome-.01):
			if(scalar or categorical):
        # should be outcome since median is the same
				p = -(abs(reportValue - median)/2) + 1
			newRep = oldRep*(2*p -1)
		# right
		else:
			if(scalar or categorical):
				p = -(abs(reportValue - median)/2) + 1
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

def proportionCorrect(event, rejected):
  if(rejected && eventActuallyRejected && rejectedPeriod && periodOver && reported && eventResolvedInCloseMarket):
		# real answer is outcome
    outcome = 2**63
    # p is proportion of correct responses
		p = 0
		if(outcome!=0):
			# binary
			if(EVENTS.getNumOutcomes(event)==2 and 2**64*EVENTS.getMaxValue(event)==2**65):
        # need to fetch uncaught outcome for rejectedperiod separately
        avgOutcome = EVENTS.getRejectedPeriodUncaught(event)
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

	if(notDoneForEvent && periodOver && reported && eventResolvedInCloseMarket):
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
	if(periodOver && reportedEnough && claimedProportionCorrectEnough && hasDoneRRForLazyEventsAndWrongAnsForPastOrGottenPenaltyBelow && hasntDoneThisAlready):
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


# "For this option I propose the appeal bond be set to":
    Appeal_Bond = Market_Value * (0.01 + Market_Fee / 2) + Average_Adjudication_Cost
    The point of Average_Adjudication_Cost is to set a floor to the appeal bond cost such that micro volume markets have a minimum appeal cost that cant be abused.
    Where:
    Average_Adjudication_Cost = Total fees paid to reporters for all markets in this reporting round   /   number of markets in this reporting round.
# Reporting period is 2 months minus 24 hours.  This 24 hours allows for the appeals to take place before the next reporting round begins.
def roundTwoBond(branch, event, eventIndex, resolving, votePeriod):
	bond = 100*2**64
  if(!self.roundTwo[event].roundTwo):
    if(SENDREP.sendReputation(branch, event, bond)==0):
      return(0)
  if(BRANCHES.getVotePeriod(branch)!=votePeriod && !resolving):
    return(0)
  eventID = EXPEVENTS.getEvent(branch, votePeriod, eventIndex)
  # if so, we're in the final 24 hours and event is in this branch + votePeriod
  if(!resolving && block.number/BRANCHES.getPeriodLength(branch)!=((block.number + 4800)/BRANCHES.getPeriodLength(branch)) && eventID!=0 && event==eventID && self.roundTwo[event].roundTwo==0):
    # makes event required reporting in round 2 (the next period) as well
    REPORTS.setEventRequired(branch, period, event)

    # push event into next period
    period = BRANCHES.getVotePeriod(branch)
    EXPIRING.addEvent(branch, period+1, event)
    # set event expiration date to be after the current reporting period ends
    EVENTS.setExpiration(event, block.number)
    MAKEREPORTS.setReportable(period+1, event)

    # set round two to true so can't be done again
    self.roundTwo[event].roundTwo = 1
    self.roundTwo[event].originalVotePeriod = votePeriod
    if(scalar or categorical):
      self.roundTwo[event].originalOutcome = EVENTS.getMedian(event)
    else:
      self.roundTwo[event].originalOutcome = catch(EVENTS.getUncaughtOutcome(event))

  # else too early or too late
  else:
    return(0)

  overruled = 1

  if(scalar or categorical):
    if(self.roundTwo[event].originalOutcome == EVENTS.getMedian(event)):
      overruled = 0
  else:
    if(self.roundTwo[event].originalOutcome == catch(EVENTS.getUncaughtOutcome(event)):
       overruled = 0

  votedOnAgain = 0

  if(BRANCHES>getVotePeriod(branch) > EVENTS.getExpiration(event) / BRANCHES.getPeriodLength(branch)):
    votedOnAgain = 1

	if(resolving && overruled && votedOnAgain && self.roundTwo[event].roundTwo && votePeriod!=self.roundTwo[event].originalVotePeriod && eventID!=0 && event==eventID):
		#a) return the bond
    # set final outcome
		#b) reward the bonded challenger with whatever rep would normally be taken from the liars up to 2x the bond, then beyond that the people who originally reported whatever the actual truth was would get the rest. then regular rbcr for the round 2 reporting
    # need to save old original outcome as well
      # so should say (if appealed don't allow rbcr until after the appeal process is over)
		setFinal
    return(2*bond)

	elif(votedOnAgain && resolving):
		lose bond
    # rbcr from original period stands, rbcr from round 2 happens as usual as well
    setFinal
    # and set final outcome

  # not voted on again yet
  else:
    return(0)


#Essentially, we could allow anyone to pay some amount significantly greater than the bond amount to force a branching event, splitting rep into two classes.  In one class the reported outcome for whatever event was the cause of dispute is said to be right, and rep would be redistributed accordingly.  In the other class/branch, the other outcome would be considered right and rep would be redistributed accordingly.  Whichever outcome was truly the correct one would determine which branch had rep that actually held value.  This would be akin to a Bitcoin hard fork scenario.  The winning fork, of course, would be the one with the most voluminous markets.  Market makers should then be able to move their market to whichever fork they want, if they fail to act, it'd go to the most voluminous fork by default after a couple weeks.
# Errors:
	# -1: round two hasn't happened yet
# what about ethics forking?
# fork scenario with scalars (1 fork has outcome, the other reports on it again is a soln)
# if readjudication says a, on fork b when rereporting, a is not a reporting option
# what if multiple things need to be forked?
# ok so the problem with a fork bond queue at all even in theory is that they're going to be forking in a worthless network.  i.e. we have parent a with child b, then b forks into b and c,  if someone in a finally gets out of the queue, they're forking a, which is a worthless network, so the markets ​_have_​ to be transferred to winning forks after some period of time.  Then, in the "winning" fork, a market could either fork the network right away again, ​_or_​ simply be readjudicated again (the latter is a cheaper option, although not guaranteed to be secure, b/c someone could be doing a long play attack per all discussion above with 10s of millions of dollars).  So if we say, ok, the market is readjudicated since it's cheaper, if ​_that_​ fails, then the network can be forked again, and so on.  This allows the long play security stuff to play out if need be, allows markets to be resolved at probably the fastest rate of these options, and still allows a sort of implicit fork queue if the network keeps forking due to a really pocket heavy attacker.
# take 20% of rep away from liars in fork, don't distribute to truthtellers until a new truthful outcome is resolved / reported


​To talk about the smaller fork bond posted:​
The fork bond is paid. Saved along with it is the current consensus that is being contested.
The bonds exist in both forks.
The market either waits for a fork or goes to back to re-adjudication, possibly more than once.
The market gets a consensus that no one appeals on the 24 hour period eventually, and the consensus is made final.
This final consensus is compared with the consensus the fork was initially done over.
a) If the final truth/consensus  is different than the one that was contested, then we know for sure the bond poster was justified in posting the fork bond, and it is handled at this point in time, paying the poster back, and collecting from the reporters that committed to the consensus the bond poster correctly identified as liars.
b) If the final truth/consensus is the same as the one that was contested, then we know for sure the bond poster contested a consensus that we know for sure was truth, and the fork bond posted was malicious. The fork bond is paid to the reporters for their additional labor.

​
12:44
has to be done on each fork too
​
12:44
i guess not if we actually assign a "final truth" --- but that's not how the fork is supposed to work
​
12:46
so each time a fork happens in one fork the cycle ends and there's an "outcome" (but the market might not be there haha) and the bond is paid or taken in that fork, and it's done differently in the other side of the fork
​
12:50
it honestly seems 100x easier to just take 80% of the rep from the liars and keep the system simple as opposed to having a tree of fork bonds...
​
12:50
on the off chance the fork gets it wrong, can just fork again
​
12:52
it's essentially what ends up happening if you keep having recursive fork bonds anyway and the work required to implement it is way less
​
12:55

paying back all the bond raisers is nice and all, but there's another lot simpler way to achieve the same effect: give the original bond raiser the right of first refusal to make another fork on the new fork after a market has been readjudicated

So.... a way to do your idea but not make it open to abuse, is to charge a non refundable cost that is the same as an appeal up to re-adjudication, along with 1% of reputation
​
5:22
this pays the reporters who have to redo the market
​
5:23
and if  the 1%  rep does not win the fork bond biding, it is returned, but the market is still contested and lives on to see another adjudication instead of resolving as is.(edited)
joeykrug
5:23 PM when do you charge that cost?
imkharn
5:24 PM Make it a pre-requisiste to sending the 1% of reputation to the fork bond contract
​
5:25
unlike all the other funds we throw at reporters however, it would have to be held in a special place while we wait for a new reporting round to begin
​
5:25
then moved into the reporters fees for that round
​
5:28
the bond paid to move from adjudication to readjudication is approximately the cost of doing a re-adjudcation full attendance report gathering.
​
5:29
oh, i see why you ask when it is charged, because one of the bids for forking will win
​
5:29
perhaps even the one paid along with the winning bid go to reporters
​
5:29
or in that case it could be refunded
​
5:29
if it is the winning fork bid

# what to do if market forked - readj. - forked again what do w/ orig readj. rep?  never happened b/c it wasn't the main fork market
def fork(event):
	if(!EVENTS.getRoundTwo(event)):
		return(-1)
	# branch 1
		# lose bond of 5k rep
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

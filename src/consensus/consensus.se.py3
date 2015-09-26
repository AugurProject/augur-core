import expiringEvents as EXPIRING
import reporting as REPORTING
import fxpFunctions as FXP
import events as EVENTS

data proportionCorrect[]

# 4\cdot x-4\cdot x^2 is parabolic function
def penalizeWrong(event):
	p = self.getProportionCorrect(event)
	outcome = EVENTS.getOutcome(event)
	for all reporters:
		if(reportValue > outcome+.01 or reportValue < outcome-.01):
			newRep = oldRep*(2*p -1)	
		else:
			newRep = 1 + oldRep*(2*(1-p)**2 / p)
		smoothedRep = oldRep*.8 + newRep*.2
	normalize(smoothedRep)
	for all reporters:
		updateRepValues();

def rewardRight(event)

def proportionCorrect():

def getProportionCorrect(event):
	return(self.proportionCorrect[event])

#So you could start off with 5000 rep, never report, and you’d “have” 5000 rep up until you tried to send it or get the balance, and all of a sudden, like Schrodinger’s cat, it’s gone (dead)!  People could ping the network to ding dead accounts (although they wouldn’t need to do so for any good reason).

# Basically, if you don't access the account, the rep just sort of sits there, proverbially speaking, it's burned.  If you access the account, it's sent to the branch's rep account, and distributed like trading fees are except each person would make their own lazy claim on it.  To prevent double claiming, similarly to trading fees each rep acc. that hadn't claimed rep or trading fees but reported that past period would neither be able to send nor receive rep until they claimed.  You'd get % of people that reported fees / rep
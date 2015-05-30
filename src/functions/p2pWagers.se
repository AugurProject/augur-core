# This software (Augur) allows buying && selling event outcomes in ethereum
# Copyright (C) 2015 Forecast Foundation
#    This program is free software; you can redistribute it &&/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is free software: you can redistribute it &&/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Any questions please contact joey@augur.net

#p2p hasn't been tested

import events as EVENTS
import cash as CASH

data p2pBets[](eventID, amtToBet, outcomeOneBettor, outcomeZeroBettor)

def getEvent(ID):
	return(self.p2pBets[ID].eventID)

def getAmtBet(ID):
	return(self.p2pBets[ID].amtToBet)

def getOutcomeOneBettor(ID):
	return(self.p2pBets[ID].outcomeOneBettor)

def getOutcomeZeroBettor(ID):
	return(self.p2pBets[ID].outcomeZeroBettor)

### P2P parimutuel betting
# @return betID
def makeBet(eventID, amtToBet):
    betData = array(3)
    betData[0] = eventID
    betData[1] = block.number
    betData[2] = tx.origin
    betID = sha256(branchinfo, chars=3*32)
    self.p2pBets[betID].eventID = betData[0]
    self.p2pBets[betID].amtToBet = amtToBet
    return(betID)

# should add a fee to market
# outcome is 0 or 1
# @return 0 if fail, 1 if success
def sendMoneytoBet(betID, outcome):
    if(CASH.balance(betID+outcome)==0):
        CASH.send(betID+outcome, self.p2pBets[betID].amtToBet)
    else:
        return(0)
    if(outcome):
        self.p2pBets[betID].outcomeOneBettor = tx.origin
    else:
        self.p2pBets[betID].outcomeZeroBettor = tx.origin
    return(1)

# add support for a .5 outcome
# @return 0 if fail, 1 if success
def closeBet(betID):
    # outcome not determined yet
    if(EVENTS.getOutcome(self.p2pBets[betID].eventID) == 0):
        return(0)
    # pay out depending on outcome
    if(CASH.balance(betID+0)==self.p2pBets[betID].amtToBet && CASH.balance(betID+1)==self.p2pBets[betID].amtToBet):
        CASH.subtractCash(betID+0, CASH.balance(betID+0))
        CASH.subtractCash(betID+1, CASH.balance(betID+1))
        if(EVENTS.getOutcome(self.p2pBets[betID].eventID)):
            CASH.addCash(self.p2pBets[betID].outcomeOneBettor, self.p2pBets[betID].amtToBet*2)
        elif(EVENTS.getOutcome(self.p2pBets[betID].eventID) == 1):
            CASH.addCash(self.p2pBets[betID].outcomeZeroBettor, self.p2pBets[betID].amtToBet*2)
    # someone didn't pay their side of the bet, refund funds
    else:
        CASH.addCash(self.p2pBets[betID].outcomeZeroBettor, CASH.balance(betID+0))
        CASH.addCash(self.p2pBets[betID].outcomeOneBettor, CASH.balance(betID+1))
        CASH.subtractCash(betID+0, CASH.balance(betID+0))
        CASH.subtractCash(betID+1, CASH.balance(betID+1))
    return(1)

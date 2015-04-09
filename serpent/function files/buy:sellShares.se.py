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

extern branches.se: [addMarket:ii:i, getBranches:_:a, getMarkets:i:a, getMinTradingFee:i:i, getNumBranches:_:i, getNumMarkets:i:i, getPeriodLength:i:i, getStep:i:i, getVotePeriod:i:i, incrementStep:i:_, initializeBranch:iiii:i]
# this really needs to be = branches.se addr., not create a new one each time
BRANCHES = create('branches.se')

extern expiringEvents.se: [addEvent:iii:i, getAdjPrinComp:ii:a, getEvent:iii:i, getEvents:ii:a, getLoadingVector:ii:a, getNewOne:ii:a, getNewTwo:ii:a, getNumberEvents:ii:i, getOutcomesFinal:ii:a, getReporterVotes:iii:a, getReportsFilled:ii:a, getReportsMask:ii:a, getScores:ii:a, getSetOne:ii:a, getSetTwo:ii:a, getSmoothRep:ii:a, getTotalRepReported:ii:i, getVSize:ii:i, getWeightedCenteredData:ii:a, returnOld:ii:a, setAdjPrinComp:iia:i, setLoadingVector:iia:i, setNewOne:iia:i, setNewTwo:iia:i, setOld:iia:i, setOutcomesFinal:iia:i, setReporterVotes:iiia:i, setReportsFilled:iia:i, setReportsMask:iia:i, setScores:iia:i, setSetOne:iia:i, setSetTwo:iia:i, setSmoothRep:iia:i, setTotalRepReported:iii:i, setVSize:iii:i, setWeightedCenteredData:iia:i]
EXPEVENTS = create('expiringEvents.se')

extern info.se: [getCreationFee:i:i, getCreator:i:i, getDescription:i:s, getDescriptionLength:i:i, setInfo:isii:i]
INFO = create('info.se')

extern cash.se: [balance:i:i, faucet:_:i, send:ii:i, sendFrom:iii:i]
CASH = create('cash.se')

extern reporting.se: [addReporter:i:i, faucet:_:_, getRepBalance:ii:i, getReputation:i:a, hashReport:ai:i, makeBallot:ii:a, reputationApi:iii:i, setInitialReporters:ii:i]
REPORTING = create('reporting.se')


macro bad_pow():
    with $data = array(4):
        $data[0] = branch
        $data[1] = market
        $data[2] = tx.origin
        $data[3] = self.nonces[tx.origin]
        with $firstHash = sha3($data, items=4):
            with $data2 = array(2):
                $data2[0] = $firstHash
                $data2[1] = nonce
                ~lt(sha3($data2, items=2), 2**254/10000)

macro inc_nonce():
    self.nonces[tx.origin] += 1

# amount of shares should be fixed point
# @return return price + fee to buy shares
# Error messages otherwise
    # -1: invalid outcome or trading closed
    # -2: entered a -amt of shares
    # -3: not enough money
    # -4: bad nonce/hash
def buyShares(branch, market, outcome, amount, nonce):
    # can trade up until the event has started to be voted on (e.g. currentVotePeriod is >= to the latest expDate/periodLength)  
    # if we have 3-4 cycles in a row of events getting pushed back market would already be closed even though events up to be decided on for a while yet never decided
    # technically this is a stalled branch and market should be open
    # if(currentPeriod + 3 >= currentVotePeriod) we're stalled
    #the question is though --- are these events part of the set that were stalled?
    #if above && the event outcomes aren't determined (0), then yes
    #then set a stalled boolean

    if bad_pow():
        return(-4)
    inc_nonce()
    stalled = 0
    if (outcome==0 || (self.Branches[branch].currentVotePeriod>=self.Markets[market].tradingPeriod && !stalled) || self.Markets[market].branch != branch):
        return(-1)
    # lmsr cost calcs
    oldCost = lsLmsr(market)
    sharesPurchased(market)[outcome] += amount
    newCost = lsLmsr(market)
    if newCost <= oldCost:
        sharesPurchased(market)[outcome] -= amount
        return(-2)
    price = (newCost - oldCost)
    
    if(self.cashcoinBalances[tx.origin] < price*(self.Markets[market].tradingFee + 2^64)/2^64):
        sharesPurchased(market)[outcome] -= amount
        return(-3)

    participantNumber = self.Markets[market].addr2participant[tx.origin]

    if(tx.origin != self.Markets[market].participants[participantNumber].participantID):
        participantNumber = self.Markets[market].currentParticipant
        self.Markets[market].participants[participantNumber].participantID = tx.origin
        self.Markets[market].addr2participant[tx.origin] = participantNumber
        self.Markets[market].currentParticipant += 1

    self.Markets[market].participants[participantNumber].shares[outcome] += amount
    # send shares of the event to user address
    # if user doesn't have enough money, revert
    # send money from user acc. to market address/account
    # cost for shares
    self.send(market, price)
    # half of fees to market creator
    fee = self.Markets[market].tradingFee*price/2^64
    self.send(self.Info[market].creator, fee/2)
    # other half go to branch
    self.send(branch, fee/2)
    return(price+fee)

# amount is amount of shares to sell
# instead of inputting particip. num could just loop through array if dont have it
# @return error msg if fail, returns amount you get paid if success
# Error messages otherwise
    # -1: invalid outcome, trading closed, or you haven't traded in this market
    # -2: entered a -amt of shares
    # -3: you own no shares 
def sellShares(branch, market, outcome, amount, nonce):
    if bad_pow():
        return(-4)
    inc_nonce()
    # can trade up until the event has started to be voted on (e.g. currentVotePeriod is >= to the latest expDate/periodLength)
    participantNumber = self.Markets[market].addr2participant[tx.origin]
    if (self.Markets[market].participants[participantNumber].participantID != tx.origin || outcome==0 || self.Branches[branch].currentVotePeriod>=self.Markets[market].tradingPeriod || self.Markets[market].branch != branch):
        return(-1)
    # lmsr cost calcs
    oldCost = lsLmsr(market)
    sharesPurchased(market)[outcome] -= amount
    newCost = lsLmsr(market)
    if oldCost <= newCost:
        sharesPurchased(market)[outcome] += amount
        return(-2)
    # these prices are in fixed point
    price = oldCost - newCost
    # remove shares from the user's account
    # if user actually doesn't have the shares, revert
    if self.Markets[market].participants[participantNumber].shares[outcome] < amount:
        sharesPurchased(market)[outcome] += amount
        return(-3)
    else:
        # send bitcoin from the market to the user acc.
        self.cashcoinBalances[market] -= price
        fee = self.Markets[market].tradingFee*price/2^64
        log(fee)
        # half of fees go to market creator
        self.cashcoinBalances[self.Info[market].creator] += fee/2
        # half go to branch
        self.cashcoinBalances[branch] += fee/2
        price -= fee
        self.cashcoinBalances[tx.origin] += price
        self.Markets[market].participants[participantNumber].shares[outcome] -= amount
        return(price)
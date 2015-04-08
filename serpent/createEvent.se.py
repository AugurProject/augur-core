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

# numOutcomes is number of outcomes for this event, e.g. quarter mile times from 10.0
# to 11.0 would be 11 outcomes (if incremented by 0.1)
# need to make sure these values are ok
# @return eventID if success
# error messages otherwise
    # -1: we're either already past that date, branch doesn't exist, or description is bad
    # 0: not enough money to pay fees or event already exists 
def createEvent(branch, description:str, expDate, minValue, maxValue, numOutcomes):
    if(self.Branches[branch].periodLength && description!=0 && expDate>block.number):
        eventinfo = string((items=8)+len(description))
        eventinfo[0] = EVENT                                        #typecode
        eventinfo[1] = branch                                       #branchID
        eventinfo[2] = expDate                                      #expiration date
        eventinfo[3] = tx.origin                                    #creator address
        eventinfo[4] = 42*2^64                                      #creation fee
        eventinfo[5] = minValue                                     #minimum outcome value
        eventinfo[6] = maxValue                                     #maximum outcome value
        eventinfo[7] = numOutcomes                                  #number of outcomes
        mcopy(eventinfo+(items=8), description, len(description))
        eventID = sha256(eventinfo, chars=len(eventinfo))
    else:
        return(-1)

    # fee to ask a question rises if voter participation (rep reported) falls, if it's really high, the fee is lowered (participationFactor is a fixedpoint number)
    participationFactor = (self.EventsExpDates[branch][self.Branches[branch].currentVotePeriod-2].totalRepReported * 2^64) / self.EventsExpDates[branch][self.Branches[branch].currentVotePeriod-1].totalRepReported
    if(participationFactor==0):
        participationFactor = 1
    # send fee and bond
    if(self.balance(tx.origin)>=(42*2^64 + participationFactor*45)):
        if (!self.Info[eventID].creator && !self.Events[eventID].branch && self.send(eventID, 42*2^64) && self.send(branch, participationFactor*45)):
            self.Info[eventID].creator = tx.origin
            self.Info[eventID].creationFee = participationFactor*45 # this is not the bond
            self.Info[eventID].descriptionLength = len(description)
            save(self.Info[eventID].description[0], description, chars=len(description))
            self.Events[eventID].branch = branch
            self.Events[eventID].expirationDate = expDate
            self.Events[eventID].minValue = minValue
            self.Events[eventID].maxValue = maxValue
            self.Events[eventID].numOutcomes = numOutcomes
            # see which future period it expires in && put the event in that bin
            # event voting periods - expDate / periodLength gives you the voting period #
            futurePeriod = (expDate / self.Branches[branch].periodLength)
            self.EventsExpDates[branch][futurePeriod].events[self.EventsExpDates[branch][futurePeriod].numberEvents] = eventID
            self.EventsExpDates[branch][futurePeriod].numberEvents += 1
            return(eventID)
        else:
            return(0)

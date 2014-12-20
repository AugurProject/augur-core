# Every entity in our contract has similar metadata.
# Instead of putting it in each entity, we put all the
# metadata here.
# Info's index is the hash of the item we're getting info on
data Info[](typecode, description[], creator, creationFee)

# CurrentVotePeriod is the current index in eventsExpDates
# LastPeriodEnd is the last voting period's block number
# Parent is the branch's parent branch.
# Branches' index is the hash of the branch (aka branchID)
# RepRequired is the amount of reputation required to reach quorem
data Branches[](currentVotePeriod, markets[], marketCount, periodLength, parent, repRequired)

# Events' index is the eventID
data Events[](branch, expirationDate, outcome)

# Reporting index is the branchID
# Reporters index is the rep. address
# We 0 index reputation so can walk thru for consensus
# EventsExpDates index is the currentVotePeriod or in the future if an event expires in the future
# RepIDtoIndex returns a reporter's reporters[] index given their reputationID as the key
data Reporting[](eventsExpDates[](numberEvents, events[], totalRepReported, reporters[][]), reputation[](repValue, reporterID), numberReporters, repIDtoIndex[])

# Markets' index is the marketID
# Events is a 0 indexed array of events in the market
# Sharespurchased keeps track of the number of shares purchased for each outcome
# Participants is a 0 indexed array of participants, their cashIDs, and the shares in each outcome they've purchased of an event
data Markets[](branch, events[](eventID, sharesPurchased[2]), participants[](participantID, event[](shares[2])), lossLimit, tradingFee, numberEvents, currentParticipant, winningEvent)

data cashcoin_balances[2^160]

nabtc $200
apple $100
owed
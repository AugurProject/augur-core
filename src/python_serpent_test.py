#!/usr/bin/env python

from __future__ import division
from ethereum import tester as t
import math
import random
import os
import time

initial_gas = 0

def test_cash():
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/cash.se')
    assert(c.initiateOwner(111)==1), "Assign owner to id=111"
    assert(c.initiateOwner(111)==0), "Do not re-assign owner of id=111"
    c.setCash(111, 10)
    gas_use(s)
    c.addCash(111,5)
    c.subtractCash(111,4)
    gas_use(s)
    assert(c.balance(111)==11), "Cash value not expected!"
    gas_use(s)
    c.send(111, 10)
    assert(c.send(47, 10)==0), "Receiver check broken"
    assert(c.balance(111)==21), "Send function broken"
    assert(c.sendFrom(101, 1, 111)==0), "Receiver uninitialized check failed"
    c.initiateOwner(101)
    assert(c.sendFrom(101, 1, 111)==1), "Send from broken"
    assert(c.balance(111)==20), "Send from broken"
    assert(c.balance(101)==1), "Send from broken"
    assert(c.setCash(447, 101)==0), "Set cash owner check broken"
    gas_use(s)
    print "CASH OK"

def test_ether():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/ether.se')
    assert(c.depositEther(value=5)==5), "Unsuccessful eth deposit"
    assert(c.withdrawEther(111, 500)==0), "Printed money out of thin air..."
    assert(c.withdrawEther(111, 5)==1), "Unsuccessful withdrawal"
    gas_use(s)
    print "ETHER OK"

def test_exp():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.setReportHash(1010101, 0, 101, 47, 0)
    assert(c.getReportHash(1010101, 0, 101, 0)==47), "Report hash wrong"
    c.addEvent(1010101, 0, 447)
    assert(c.getEvent(1010101, 0, 0) == 447), "Add/get event broken"
    assert(c.getNumberEvents(1010101, 0)==1), "Num events wrong"
    assert(c.setNumEventsToReportOn(1010101, 0)==-1), "Vote period check issue"
    c.moveEventsToCurrentPeriod(1010101, 1, 2)
    assert(c.getEvent(1010101, 2, 0) == 447), "Move events broken"
    assert(c.sqrt(25*2**64)==5*2**64), "Square root broken"
    print "EXPIRING EVENTS OK"
    gas_use(s)

def test_log_exp():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/fxpFunctions.se')
    assert(c.fx_exp(2**64) == 50143449209799256664), "Exp broken"
    assert(c.fx_log(2**64) == 7685), "Log broken"
    print "LOG EXP OK"
    xs = [2**64, 2**80, 2**68, 2**70]
    maximum = max(xs)
    sum = 0
    original_method_sum = 0
    i = 0
    while i < len(xs):
        sum += c.fx_exp(xs[i] - maximum)
        original_method_sum += c.fx_exp(xs[i])
        i += 1
    print maximum + c.fx_log(sum)
    print c.fx_log(original_method_sum)
    gas_use(s)

def test_markets():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initializeMarket(444, [445, 446, 447], 1, 2**57, 1010101, 2)
    c.initialLiquiditySetup(444, 2**55, 1, 2)
    c.setWinningOutcomes(444, [2])
    assert(c.getWinningOutcomes(444)[0] == 2), "Winning outcomes wrong"
    assert(c.addParticipant(444, s.block.coinbase)==0), "Participant adding issue"
    # getMarketEvent singular
    assert(c.getParticipantNumber(444, s.block.coinbase)==0), "Participant number issue"
    assert(c.getParticipantID(444, 0)==745948140856946866108753121277737810491401257713), "Participant ID issue"
    assert(c.getMarketEvents(444) == [445,446,447]), "Market events load/save broken"
    print "MARKETS OK"

def test_reporting():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    assert(c.getRepByIndex(1010101, 0) == 47*2**64), "Get rep broken"
    assert(c.getReporterID(1010101, 1)==1010101), "Get reporter ID broken"
    #c.getReputation(address)
    assert(c.repIDToIndex(1010101, 1010101)==1), "Rep ID to index wrong"
    #c.claimInitialRep(parent, newBranch)
    c.addReporter(1010101, 777)
    c.addRep(1010101, 2, 55*2**64)
    c.subtractRep(1010101, 2, 2**64)
    assert(c.getRepByIndex(1010101, 2) == 54*2**64), "Get rep broken upon adding new reporter"
    assert(c.getReporterID(1010101, 2)==777), "Get reporter ID broken upon adding new reporter"
    assert(c.repIDToIndex(1010101, 777)==2), "Rep ID to index wrong upon adding new reporter"
    c.setRep(1010101, 2, 5*2**64)
    assert(c.getRepBalance(1010101, 777) == 5*2**64), "Get rep broken upon set rep"
    c.addDormantRep(1010101, 2, 5)
    c.subtractDormantRep(1010101, 2, 2)
    assert(c.balanceOf(1010101, 777)==3), "Dormant rep balance broken"
    assert(c.getDormantRepByIndex(1010101, 2)==3), "Dormant rep by index broken"
    gas_use(s)
    c.setSaleDistribution([4,44,444,4444,44444], [0, 1, 2, 3, 4], 1010101)
    assert(c.getRepBalance(1010101, 4444)==3), "Rep Balance fetch broken w/ initial distrib."
    assert(c.getReporterID(1010101, 6)==4444), "Sale distrib. reporter ID wrong"
    print "REPORTING OK"

def test_create_branch():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    b = c.createSubbranch("new branch", 100, 1010101, 2**55, 0)
    assert(b<-3 or b>3), "Branch creation fail"
    assert(c.createSubbranch("new branch", 100, 1010101, 2**55, 0)==-2), "Branch already exist fail"
    assert(c.createSubbranch("new branch", 100, 10101, 2**55, 0)==-1), "Branch doesn't exist check fail"
    assert(c.getParentPeriod(b)==c.getVotePeriod(1010101)), "Parent period saving broken"
    event1 = c.createEvent(b, "new event", 555, 1, 2, 2)
    print hex(event1)
    bin_market = c.createMarket(b, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    print hex(bin_market)
    print "Test branch OK"

def test_send_rep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    assert(c.sendReputation(1010101, s.block.coinbase, 444)==444), "Send rep failure"
    assert(c.sendReputation(1010101, 1010101, 444)==444), "Send rep failure"
    assert(c.sendReputation(1010101, 999, 444)==-2), "Send rep to nonexistant receiver check failure"
    assert(c.sendReputation(1010101, s.block.coinbase, 1000000*2**64)==0), "Send rep user doesn't have check failure"
    assert(c.convertToDormantRep(1010101, 500*2**64)==0), "Allowed converting a bunch of rep to dormant that user didn't have"
    assert(c.convertToDormantRep(1010101, 444)==444), "Dormant rep conversion unsuccessful"
    assert(c.convertToActiveRep(1010101, 500*2**64)==0), "Allowed converting a bunch of rep to active that user didn't have"
    assert(c.convertToActiveRep(1010101, 400)==400), "Active rep conversion unsuccessful"
    assert(c.sendDormantRep(1010101, s.block.coinbase, 444)==0), "Send dormant rep user didn't have check failure"
    assert(c.sendDormantRep(1010101, s.block.coinbase, 10)==10), "Send dormant rep user failure"
    assert(c.sendDormantRep(1010101, 999, 10)==-2), "Send dormant rep to nonexistant receiver check failure"
    assert(c.balanceOf(1010101, s.block.coinbase)==44), "Dormant rep balance off"
    assert(c.getRepBalance(1010101, s.block.coinbase)==866996971464348925464), "Rep balance off"
    print "Test send rep OK"

def nearly_equal(a,b,sig_fig=8):
    return(a==b or int(a*10**sig_fig) == int(b*10**sig_fig))
    
def isclose(a, b, rel_tol=1e-8, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def test_trading():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    i = -1
    while i < 50:
        if(i==0):
            i+=2
            continue
        gas_use(s)
        
        blocktime = s.block.timestamp + 500
        # covers binary + scalar events
        e = c.createEvent(1010101, "event"+str(i), blocktime+1, i*2**64, i*i*2**64, 2, "soisoisoi.com")
        m = c.createEvent(1010101, "sdevent"+str(i), blocktime+1, i*2**64, i*i*2**64, 2, "soisoisoi.com")
        n = c.createEvent(1010101, "sdeventn"+str(i), blocktime+1, i*2**64, i*i*2**64, 2, "soisoisoi.com")
        print "Event creation gas use"
        print gas_use(s)
        print e
        print m
        print n
        assert(e>1 or e<-9), "Event creation broken"
        # covers categorical
        f = c.createEvent(1010101, "event"+str(i), blocktime+1, i*2**64, i*i*2**64, 3, "soisoisoi.com")
        assert(f>0 or f<-9), "binary Event creation broken"
        feeSplit = int(random.random()*2**63)
        gas_use(s)
        bin_market = c.createMarket(1010101, "new market", 184467440737095516, [e], 1, 2, 3, feeSplit, "yayaya", value=10**19)
        print "Market creation gas use"
        print gas_use(s)
        assert(bin_market>0 or bin_market<-9), "market creation broken"
        twodmarket = c.createMarket(1010101, "new market", 184467440737095516, [e, f], 1, 2, 3, feeSplit, "yayaya", value=10**19)
        assert(twodmarket>0 or twodmarket<-9), "market creation broken"
        threedmarket = c.createMarket(1010101, "new market", 184467440737095516, [e, m, n], 1, 2, 3, feeSplit, "yayaya", value=10**19)
        assert(threedmarket>0 or threedmarket<-9), "market creation broken"
        market = [bin_market, twodmarket, threedmarket]
        maxValue = i*i*2**64
        minValue = i*2**64
        cumScale = []
        if(maxValue!=2**65 or minValue!=2**64):
            cumScale = [maxValue-minValue, maxValue-minValue, 3*(maxValue-minValue)]
        else:
            cumScale = [2**64, 2**64, 2**64]
        a = 0
        while a < 3:
            initialBranchBal = c.balance(1010101)
            # set cash to 100k initially for both k1 and k2
            c.setCash(s.block.coinbase, 100000*2**64)
            sender2 = c.getSender(sender=t.k2)
            c.setCash(sender2, 100000*2**64)
            # to calc costs need data to do fee calc and whether maker or not etc.
            feePercent = 4 * c.getTradingFee(market[a]) * .01 * 2**64 * (2**64-.01*2**64*2**64/cumScale[a]) / (2**64*cumScale[a])
            fee = .01*2**64 * feePercent / 2**64
            # THREEFOURTHS is 3/4
            branchFees = (.75*2**64 + (.5*2**64 - c.getMakerFees(market[a]))/2)*fee / 2**64
            creatorFees = (.25*2**64 + (.5*2**64 - c.getMakerFees(market[a]))/2)*fee / 2**64
            takerFeesTotal = branchFees + creatorFees
            
            # other party [maker] pay their part of the fee here too
            makerFee = fee * c.getMakerFees(market[a]) / 2**64
            makerFee = int(makerFee)
            assert(c.balance(s.block.coinbase)==100000*2**64)
            assert(c.balance(sender2)==100000*2**64)
            gas_use(s)
            assert(c.getCumScale(market[a])==cumScale[a])
            assert(c.buyCompleteSets(market[a], 10*2**64)==1)
            assert(c.balance(s.block.coinbase)==(100000*2**64 - 10*cumScale[a]))
            print c.balance(s.block.coinbase)
            print "Buy complete sets gas use"
            print gas_use(s)
            if(a==2):
                sellin = c.sell(2**64, int(.01*2**64), market[2], 3)
                assert(c.cancel(sellin)==1)
            assert(c.sellCompleteSets(market[a], 8*2**64)==1)
            assert(c.balance(s.block.coinbase)==(100000*2**64 - 2*cumScale[a]))
            assert(c.balance(market[a])==2*cumScale[a])
            print "Sell complete sets gas use"
            print gas_use(s)
            print "market vol"
            assert(c.getVolume(market[a])==18*c.getMarketNumOutcomes(market[a])*2**64)
            assert(c.getSharesValue(market[a])==c.getCumScale(market[a])*2)
            assert(c.getTotalSharesPurchased(market[a])==2*c.getMarketNumOutcomes(market[a])*2**64)
            participantNumberIDK1 = c.getParticipantNumber(market[a], s.block.coinbase)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**65)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==2**65)
            assert(c.getSharesPurchased(market[a], 1)==2**65)
            assert(c.getSharesPurchased(market[a], 2)==2**65)
            # get cash balance before and after, ask is just fee
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            gas_use(s)
            sell = c.sell(2**64, int(.01*2**64), market[a], 1)
            print "selling gas use"
            print gas_use(s)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==2**65)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(len(c.get_trade_ids(market[a]))==1)
            assert(isclose((before-after)/2**64, makerFee/2**64, rel_tol=1e-10))
            assert(isclose((afterm-beforem)/2**64, makerFee/2**64, rel_tol=1e-10))
            gas_use(s)
            c.cancel(sell)
            print "Cancel gas use"
            print gas_use(s)
            afterm = c.balance(market[a])
            after = c.balance(s.block.coinbase)
            assert(nearly_equal((before-after), 0))
            assert(nearly_equal((beforem-afterm), 0))
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**65)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==2**65)
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            sell = c.sell(2**64, int(.01*2**64), market[a], 1)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==2**65)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/2**64, makerFee/2**64, rel_tol=1e-10))
            assert(isclose((afterm-beforem)/2**64, makerFee/2**64, rel_tol=1e-10))
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            gas_use(s)
            # get cash balance before and after, bid includes cost + fee
            buy = c.buy(2**64, int(.01*2**64), market[a], 2)
            print "Buy gas use"
            gas_use(s)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/2**64, (makerFee + 2**64*.01)/2**64, rel_tol=1e-10))
            assert(isclose((afterm-beforem)/2**64, (makerFee + 2**64*.01)/2**64, rel_tol=1e-10))
            assert(len(c.get_trade_ids(market[a]))==2)
            # make sure got cost + fee back
            c.cancel(buy)
            afterm = c.balance(market[a])
            after = c.balance(s.block.coinbase)
            assert(nearly_equal((before-after), 0))
            assert(nearly_equal((beforem-afterm), 0))
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            buy = c.buy(2**64, int(.01*2**64), market[a], 2)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/2**64, (makerFee + 2**64*.01)/2**64, rel_tol=1e-10))
            assert(isclose((afterm-beforem)/2**64, (makerFee + 2**64*.01)/2**64))
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==2**65)
            hash = c.makeTradeHash(0, 2**64, [buy], sender=t.k2)
            c.commitTrade(hash, sender=t.k2)
            s.mine(1)
            c.buyCompleteSets(market[a], 10*2**64, sender=t.k2)
            assert(c.getParticipantSharesPurchased(market[a], 1, 1)==10*2**64)
            assert(c.getParticipantSharesPurchased(market[a], 1, 2)==10*2**64)

            before = c.balance(sender2)
            beforem = c.balance(market[a])
            # make sure buyer got their shares, make sure seller or k2 got cash & got rid of their shares
            gas_use(s)
            x = c.trade(0, 2**64, [buy], sender=t.k2)
            print "Trade gas use"
            gas_use(s)
            assert(x[2]==1)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            assert(isclose((after-before)/2**64, (2**64*.01-fee*(1+((2**63-c.getMakerFees(market[a]))/2**64)))/2**64))
            assert(isclose((beforem-afterm)/2**64, (2**64*.01+makerFee)/2**64))
            assert(c.getParticipantSharesPurchased(market[a], 1, 1)==10*2**64)
            assert(c.getParticipantSharesPurchased(market[a], 1, 2)==9*2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==3*2**64)
            hash = c.makeTradeHash(2**64, 0, [sell], sender=t.k2)
            c.commitTrade(hash, sender=t.k2)
            s.mine(1)
            # make sure buyer or k2 got their shares and gets rid of cash, make sure seller got cash & got rid of their shares
            assert(c.getParticipantSharesPurchased(market[a], 1, 1)==10*2**64)
            assert(c.getParticipantSharesPurchased(market[a], 1, 2)==9*2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==3*2**64)
            before = c.balance(sender2)
            beforem = c.balance(market[a])
            beforeog = c.balance(s.block.coinbase)
            gas_use(s)
            assert(c.trade(2**64, 0, [sell], sender=t.k2)[2]==1)
            print "Trade gas use"
            gas_use(s)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            afterog = c.balance(s.block.coinbase)
            assert(isclose((before-after)/2**64, (2**64*.01+fee*(1+((2**63-c.getMakerFees(market[a]))/2**64)))/2**64))
            print "Hmmmmmmmm"
            print beforem
            print afterm
            print beforem - afterm
            print makerFee
            assert(isclose((beforem-afterm)/2**64, makerFee/2**64))
            # b/c this is also creator who gets part of maker fee from maker [himself] and creator fee from taker
            assert(isclose((afterog-beforeog)/2**64, (2**64*.01 + creatorFees + makerFee/2)/2**64))
            assert(c.getParticipantSharesPurchased(market[a], 1, 1)==11*2**64)
            assert(c.getParticipantSharesPurchased(market[a], 1, 2)==9*2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==3*2**64)
            # after putting order on book
            assert(len(c.get_trade_ids(market[a]))==0)

            assert(nearly_equal(c.getTotalSharesPurchased(market[a]), 12*c.getMarketNumOutcomes(market[a])*2**64))
            assert(nearly_equal(c.getSharesValue(market[a]), c.getCumScale(market[a])*12))
            assert(nearly_equal(c.getVolume(market[a]), (4*2**64 + 28*c.getMarketNumOutcomes(market[a])*2**64)))
            assert(isclose((c.balance(1010101)-initialBranchBal)/2**64, fee*2/2**64))
            # complete sets #*cumscale or 12*cumscale
            assert(isclose(c.balance(market[a])/2**64, 12*cumScale[a]/2**64))
            buy = c.buy(2**64, int(.01*2**64), market[a], 1, sender=t.k2)
            # Example:
                #buyer gives up say 20
                #complete set cost is say 100
                #fee is say 2
                #market should lose 20 from buyer's escrowed money
                #market should gain 100 from complete set
                #market also loses maker fee
                #person short selling should give the market 80 [complete set cost less shares sold]
                #plus fees
                    #1 should go to branch
                    #1 should go to creator
            before = c.balance(sender2)
            beforem = c.balance(market[a])
            beforeog = c.balance(s.block.coinbase)
            hash = c.makeTradeHash(0, 2**64, [buy])
            c.commitTrade(hash)
            s.mine(1)
            gas_use(s)
            assert(c.short_sell(buy, 2**64)[2]==1)
            assert(c.getParticipantSharesPurchased(market[a], 1, 1)==12*2**64)
            assert(c.getParticipantSharesPurchased(market[a], 1, 2)==9*2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 1)==2**64)
            assert(c.getParticipantSharesPurchased(market[a], participantNumberIDK1, 2)==4*2**64)
            print "Short sell gas use"
            gas_use(s)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            afterog = c.balance(s.block.coinbase)
            assert(isclose((afterm-beforem)/2**64, (cumScale[a]-.01*2**64 - makerFee)/2**64))
            # lose cost for complete sets and branchfees, creator fees paid by you go back to you, makerfees/2 go to you, get money back from buy order you filled
            assert(isclose((beforeog-afterog)/2**64, (cumScale[a]-.01*2**64+branchFees-makerFee/2)/2**64)==1)
            assert(isclose((beforeog-afterog)/2**64, (cumScale[a]-.01*2**64+branchFees-makerFee/2)/2**64))
            a += 1
        i += 1
    print "BUY AND SELL OK"
    return(1)

def test_close_market():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    i = c.getVotePeriod(1010101)
    while i < (s.block.timestamp/c.getPeriodLength(1010101)-1):
        c.incrementPeriod(1010101)
        i += 1
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, [event1], 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new ok event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new matrket", 184467440737095516, [event2], 1, 2, 3, 0, "yayaya", value=10**19)
    event3 = c.createEvent(1010101, "new sdok event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market3 = c.createMarket(1010101, "new matrket", 184467440737095516, [event3], 1, 2, 3, 0, "yayaya", value=10**19)
    event4 = c.createEvent(1010101, "newsdf sdok event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market4 = c.createMarket(1010101, "new matrket", 184467440737095516, [event4], 1, 2, 3, 0, "yayaya", value=10**19)

    # categorical
    event5 = c.createEvent(1010101, "new sdokdf event", blocktime+1, 2**64, 5*2**64, 3, "ok")
    # scalar
    event6 = c.createEvent(1010101, "new sdokdf mevent", blocktime+1, -100*2**64, 200*2**64, 2, "ok")

    market5 = c.createMarket(1010101, "new market", 184467440737095516, [event5, event6], 1, 2, 3, 0, "yayaya", value=10**19)
    c.cashFaucet(sender=t.k2)
    print c.buyCompleteSets(bin_market2, 10*2**64, sender=t.k2)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < (int((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1

    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    report_hash = c.makeHash(0, 2**64, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*2**64, event2, s.block.coinbase)
    report_hash3 = c.makeHash(0, 2*2**64, event3, s.block.coinbase)
    report_hash4 = c.makeHash(0, 3*2**63, event4, s.block.coinbase)
    assert(c.submitReportHash(event1, report_hash)==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2)==1), "Report hash submission failed"
    assert(c.submitReportHash(event4, report_hash4)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event2, 0, 2*2**64, 2**64)==1), "Report submission failed"
    assert(c.submitReport(event4, 0, 3*2**63, 2**64)==1), "Report submission failed"
    c.send(market5, 2**64)
    assert(c.closeMarket(1010101, market5)==0), "Not expired check [and not early resolve due to not enough reports submitted check] broken"
    assert(c.submitReport(event1, 0, 2**64, 2**64)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    c.setUncaughtOutcome(event1, 0)
    c.setOutcome(event1, 0)
    c.send(bin_market, 2**64)
    assert(c.closeMarket(1010101, bin_market)==-2), "No outcome on market yet"
    c.setUncaughtOutcome(event1, 3*2**63)
    c.setOutcome(event1, 3*2**63)
    assert(c.closeMarket(1010101, bin_market)==0), "Already resolved indeterminate market check fail"
    assert(c.closeMarket(1010101, bin_market4)==-1)
    orig = c.balance(s.block.coinbase)
    bond = c.balance(event2)
    assert(c.balance(bin_market2)==10*2**64)
    gas_use(s)
    assert(c.closeMarket(1010101, bin_market2)==1), "Close market failure"
    print "Close market binary gas use"
    gas_use(s)
    new = c.balance(s.block.coinbase)
    origK = c.balance(c.getSender(sender=t.k2))
    # get 1/2 of liquidity (50) + 42 for event bond
    assert((new - orig)==bond), "Event bond not returned properly"
    assert(c.balance(bin_market2)==10*2**64), "Should only be winning shares remaining issue"
    assert(c.balance(event2)==0)
    # ensure proceeds returned properly
    assert(c.claimProceeds(1010101, bin_market2, sender=t.k2)==1)
    newK = c.balance(c.getSender(sender=t.k2))
    assert((newK - origK)==10*2**64), "Didn't get 10 back from selling winning shares"
    assert(c.balance(bin_market2)==0), "Payouts not done successfully"
    gas_use(s)
    gas_use(s)
    print "Test close market OK"

def test_consensus():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+1, 2**64, 2*2**64, 2, "www.roflcopter.com")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, [event1], 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, 2**64, 2*2**64, 2, "buddyholly.com")
    bin_market2 = c.createMarket(1010101, "new market", 184467440737095516, [event2], 1, 2, 3, 0, "yayaya", value=10**19)
    s.mine(1)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < int((s.block.timestamp+1)/c.getPeriodLength(1010101)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    report_hash = c.makeHash(0, 2**64, event1, s.block.coinbase)
    gas_use(s)
    report_hash2 = c.makeHash(0, 2*2**64, event2, s.block.coinbase)
    gas_use(s)
    assert(c.submitReportHash(event1, report_hash)==1), "Report hash submission failed"
    print "hash submit gas use"
    gas_use(s)
    assert(c.submitReportHash(event2, report_hash2)==1), "Report hash submission failed"
    print "hash submit gas use"
    gas_use(s)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, 2**64, 2**64)==1), "Report submission failed"
    print "report submit gas use"
    gas_use(s)
    assert(c.submitReport(event2, 0, 2*2**64, 2**64)==1), "Report submission failed"
    print "report submit gas use"
    gas_use(s)
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = int((blocktime+1)/c.getPeriodLength(1010101))
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*2**64)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*2**64)
    gas_use(s)
    assert(c.penalizeNotEnoughReports(1010101)==1)
    print "Not enough reports penalization gas cost"
    gas_use(s)
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*2**64)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.getTotalRep(branch)==47*2**64)
    # need to resolve event first
    c.send(bin_market, 5*2**64)
    c.send(bin_market2, 5*2**64)
    gas_use(s)
    #votingPeriodEvent = int(c.getExpiration(event1)/c.getPeriodLength(branch))
    #fxpOutcome = c.getOutcome(event1)
    #c.getReportable(votingPeriodEvent, event1)
    #c.getUncaughtOutcome(event1)
    #c.getRoundTwo(event1)
    #c.getFinal(event1)
    #forkPeriod = c.getForkPeriod(c.getEventBranch(event1))
    #currentPeriod = int(s.block.timestamp/c.getPeriodLength(branch))
    #c.getForked(event1)
    #c.getForkedDone(event1)
    #c.getMaxValue(event1)
    #c.getMinValue(event1)
    #c.getNumOutcomes(event1)
    #print c.resolveBinary(event1, bin_market, branch, votingPeriodEvent, c.getVotePeriod(branch))
    #print "gas use for resolving 1 event"
    #gas_use(s)
    assert(c.closeMarket(1010101, bin_market)==1)
    print "close market gas use"
    gas_use(s)
    assert(c.closeMarket(1010101, bin_market2)==1)
    print "close market gas use"
    gas_use(s)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    gas_use(s)
    assert(c.penalizeWrong(1010101, event1)==1)
    print "Penalize wrong gas cost"
    gas_use(s)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "Test consensus OK"

def test_slashrep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, [event1], 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new market2", 184467440737095516, [event2], 1, 2, 3, 0, "ayayaya", value=10**19)
    i = c.getVotePeriod(1010101)
    while i < (int((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    report_hash = c.makeHash(0, 2**64, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*2**64, event2, s.block.coinbase)
    print c.submitReportHash(event1, report_hash)
    print c.getVotePeriod(1010101)
    print blocktime / 15
    print s.block.timestamp / 15
    print s.block.timestamp % 15
    #assert(==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2)==1), "Report hash submission failed"
    c.slashRep(1010101, 0, 2**64, s.block.coinbase, event1, 1)
    s.mine(1)
    periodLength = c.getPeriodLength(1010101)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, 2**64, 2**64)==1), "Report submission failed"
    assert(c.submitReport(event2, 0, 2*2**64, 2**64)==1), "Report submission failed"
    s.mine(1)
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = c.getVotePeriod(1010101) - 1
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==0)
    
    assert(c.penalizeNotEnoughReports(1010101)==1)
    
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==0)
    # need to resolve event first
    c.send(bin_market, 2**64)
    c.send(bin_market2, 2**64)
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)

    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event1)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getRepBalance(branch, s.block.coinbase)==int(23.5*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getRepBalance(branch, s.block.coinbase)==int(23.5*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "Test slashrep OK"

def test_claimrep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    c.setBeforeRep(1010101, c.getVotePeriod(1010101), 47*2**64, s.block.coinbase)
    newBranch = c.createSubbranch("new branch", 500, 1010101, 2**54, 0)
    assert(c.claimInitialRep(1010101, newBranch)==1)
    assert(c.sendReputation(newBranch, s.block.coinbase, 444)==444)
    print "Test claimrep OK"

def test_catchup():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    s.mine(1)
    print s.block.timestamp
    time.sleep(20)
    s.mine(20)
    i = c.getVotePeriod(1010101)
    origi = i
    while i < int((s.block.timestamp/c.getPeriodLength(1010101)-1)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    blocktime = s.block.timestamp
    assert(c.penalizationCatchup(1010101)==1)
    diffInPeriods = i - origi
    diffInPeriods = min(diffInPeriods, 22)
    print blocktime
    print c.getVotePeriod(1010101)
    print blocktime / 15
    # blocktime / 15 should be 1 greater than votePeriod but for some reason i think it isn't
    assert(isclose(c.getRepBalance(1010101, s.block.coinbase)/2**64, 47*.99**diffInPeriods*2**64/2**64))
    event1 = c.createEvent(1010101, "new event", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, [event1], 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, 2**64, 2**65, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new market2", 184467440737095516, [event2], 1, 2, 3, 0, "ayayaya", value=10**19)
    report_hash = c.makeHash(0, 2**64, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*2**64, event2, s.block.coinbase)
    i = c.getVotePeriod(1010101)
    while i < int(((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1
    periodLength = c.getPeriodLength(1010101)
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    n = c.submitReportHash(event1, report_hash)
    print n
    print s.block.timestamp
    assert(n==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, 2**64, 2**64)==1), "Report submission failed"
    assert(c.submitReport(event2, 0, 2*2**64, 2**64)==1), "Report submission failed"
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = c.getVotePeriod(1010101)-1
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    print c.getRepBalance(branch, branch)
    assert(isclose(c.getRepBalance(branch, branch)/2**64, ((47*2**64 - 47*.99**diffInPeriods*2**64)/2**64)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    print s.block.timestamp
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    print s.block.timestamp
    assert(c.penalizeNotEnoughReports(1010101)==1)

    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(isclose(c.getRepBalance(branch, branch)/2**64, ((47*2**64 - 47*.99**diffInPeriods*2**64)/2**64)))
    assert(c.getTotalRep(branch)==866996971464348925952)

    # need to resolve event first
    c.send(bin_market, 2**64)
    c.send(bin_market2, 2**64)
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)
    
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(isclose(c.getRepBalance(branch, branch)/2**64, ((47*2**64 - 47*.99**diffInPeriods*2**64)/2**64)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.penalizeWrong(1010101, event1)==1)

    print c.getBeforeRep(branch, period, s.block.coinbase)
    assert(isclose(c.getBeforeRep(branch, period, s.block.coinbase)/2**64, 47*.99**diffInPeriods*2**64/2**64))
    assert(isclose(c.getRepBalance(branch, s.block.coinbase)/2**64, 47*.99**diffInPeriods*2**64/2**64))
    assert(isclose(c.getRepBalance(branch, branch)/2**64, ((47*2**64 - 47*.99**diffInPeriods*2**64)/2**64)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.penalizeWrong(1010101, event2)==1)
    
    assert(isclose(c.getBeforeRep(branch, period, s.block.coinbase)/2**64, 47*.99**diffInPeriods*2**64/2**64))
    assert(isclose(c.getRepBalance(branch, s.block.coinbase)/2**64, 47*.99**diffInPeriods*2**64/2**64))
    assert(isclose(c.getRepBalance(branch, branch)/2**64, ((47*2**64 - 47*.99**diffInPeriods*2**64)/2**64)))
    assert(c.getTotalRep(branch)==47*2**64)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101)==1)
    assert(c.getRepBalance(branch, s.block.coinbase)==866996971464348925952)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==866996971464348925952)
    print "Test catchup OK"

def gas_use(s):
    global initial_gas
    print "Gas Used:"
    print s.block.gas_used - initial_gas
    initial_gas = s.block.gas_used

if __name__ == '__main__':
    src = os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace', 'src')
    os.system('rm functions/output.se')
    os.system('python mk_test_file.py \'' + os.path.join(src, 'functions') + '\' \'' + os.path.join(src, 'data_api') + '\' \'' + os.path.join(src, 'functions') + '\'')
    # data/api tests
    #test_cash()
    #test_ether()
    #test_quicksort()
    #test_insertionsort()
    #test_log_exp()
    #test_exp()
    #test_markets()
    #test_reporting()

    # function tests
    #test_create_event()
    #test_create_market()
    #test_trading()
    #test_transfer_shares()
    #test_create_branch()
    #test_send_rep()
    #test_make_reports()
    test_close_market()
    #test_consensus()
    #test_catchup()
    #test_slashrep()
    #test_claimrep()
    print "DONE TESTING"
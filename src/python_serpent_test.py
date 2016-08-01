#!/usr/bin/env python

from __future__ import division
from ethereum import tester as t
import math
import random
import os
import time
from pprint import pprint

initial_gas = 0

ONE = 10**18
TWO = 2*ONE
HALF = ONE/2

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
    assert(c.balance(111)==21), "Send function broken"
    c.initiateOwner(101)
    assert(c.sendFrom(101, 1, 111)==1), "Send from broken"
    assert(c.balance(111)==20), "Send from broken"
    assert(c.balance(101)==1), "Send from broken"
    gas_use(s)
    print "CASH OK"

def test_ether():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('need_addl_testing/ether.se')
    print c.depositEther(value=5)
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
    assert(c.sqrt(25*ONE)==5*ONE), "Square root broken"
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
    c.initializeMarket(444, [445, 446, 447], 1, 2**57, 1010101, 1, 2, 3, 2**58, ONE, 2, "aaa", 500, 20*ONE, 2222)
    c.setWinningOutcomes(444, [2])
    assert(c.getWinningOutcomes(444)[0] == 2), "Winning outcomes wrong"
    # getMarketEvent singular
    assert(c.getMarketEvents(444) == [445, 446, 447]), "Market events load/save broken"
    print "MARKETS OK"

def test_reporting():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    assert(c.getRepByIndex(1010101, 0) == 47*ONE), "Get rep broken"
    assert(c.getReporterID(1010101, 1)==1010101), "Get reporter ID broken"
    #c.getReputation(address)
    assert(c.repIDToIndex(1010101, 1010101)==1), "Rep ID to index wrong"
    #c.claimInitialRep(parent, newBranch)
    c.addReporter(1010101, 777)
    c.addRep(1010101, 2, 55*ONE)
    c.subtractRep(1010101, 2, ONE)
    assert(c.getRepByIndex(1010101, 2) == 54*ONE), "Get rep broken upon adding new reporter"
    assert(c.getReporterID(1010101, 2)==777), "Get reporter ID broken upon adding new reporter"
    assert(c.repIDToIndex(1010101, 777)==2), "Rep ID to index wrong upon adding new reporter"
    c.setRep(1010101, 2, 5*ONE)
    assert(c.getRepBalance(1010101, 777) == 5*ONE), "Get rep broken upon set rep"
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
    c.cashFaucet()
    event1 = c.createEvent(b, "new event", s.block.timestamp+50, ONE, TWO, 2, "hehe")
    print hex(event1)
    bin_market = c.createMarket(b, "new market", 2**58, [event1], 1, 2, 3, 2**60, "hehehe", value=10**18)
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
    assert(c.sendReputation(1010101, s.block.coinbase, 1000000*ONE)==0), "Send rep user doesn't have check failure"
    assert(c.convertToDormantRep(1010101, 500*ONE)==0), "Allowed converting a bunch of rep to dormant that user didn't have"
    assert(c.convertToDormantRep(1010101, 444)==444), "Dormant rep conversion unsuccessful"
    assert(c.convertToActiveRep(1010101, 500*ONE)==0), "Allowed converting a bunch of rep to active that user didn't have"
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
        e = c.createEvent(1010101, "event"+str(i), blocktime+1, i*ONE, i*i*ONE, 2, "soisoisoi.com")
        m = c.createEvent(1010101, "sdevent"+str(i), blocktime+1, i*ONE, i*i*ONE, 2, "soisoisoi.com")
        n = c.createEvent(1010101, "sdeventn"+str(i), blocktime+1, i*ONE, i*i*ONE, 2, "soisoisoi.com")
        print "Event creation gas use"
        print gas_use(s)
        print e
        print m
        print n
        assert(e>1 or e<-9), "Event creation broken"
        # covers categorical
        f = c.createEvent(1010101, "event"+str(i), blocktime+1, i*ONE, i*i*ONE, 3, "soisoisoi.com")
        assert(f>0 or f<-9), "binary Event creation broken"
        feeSplit = int(random.random()*HALF)
        gas_use(s)
        bin_market = c.createMarket(1010101, "new market", 184467440737095516, e, 1, 2, 3, feeSplit, "yayaya", value=10**19)
        cat_market = c.createMarket(1010101, "new markesst", 184467440737095516, f, 4, 2, 3, feeSplit, "yayaya", value=10**19)
        print "Market creation gas use"
        print gas_use(s)
        assert(bin_market>0 or bin_market<-9), "market creation broken"
        market = [bin_market, cat_market]
        maxValue = i*i*ONE
        minValue = i*ONE
        cumScale = []
        if(maxValue!=TWO or minValue!=ONE):
            cumScale = [maxValue-minValue, ONE]
        else:
            cumScale = [ONE, ONE]
        a = 0
        while a < 2:
            initialBranchBal = c.balance(1010101)
            # set cash to 100k initially for both k1 and k2
            c.setCash(s.block.coinbase, 100000*ONE)
            sender2 = c.getSender(sender=t.k2)
            c.setCash(sender2, 100000*ONE)
            # to calc costs need data to do fee calc and whether maker or not etc.
            feePercent = 4 * c.getTradingFee(market[a]) * .01 * ONE * (ONE-.01*ONE*ONE/cumScale[a]) / (ONE*cumScale[a])
            fee = .01*ONE * feePercent / ONE
            # THREEFOURTHS is 3/4
            branchFees = (.75*ONE + (.5*ONE - c.getMakerFees(market[a]))/2)*fee / ONE
            creatorFees = (.25*ONE + (.5*ONE - c.getMakerFees(market[a]))/2)*fee / ONE
            takerFeesTotal = branchFees + creatorFees
            
            # other party [maker] pay their part of the fee here too
            makerFee = fee * c.getMakerFees(market[a]) / ONE
            makerFee = int(makerFee)
            assert(c.balance(s.block.coinbase)==100000*ONE)
            assert(c.balance(sender2)==100000*ONE)
            gas_use(s)
            assert(c.getCumScale(market[a])==cumScale[a])
            assert(c.buyCompleteSets(market[a], 10*ONE)==1)
            assert(c.balance(s.block.coinbase)==(100000*ONE - 10*cumScale[a]))
            print c.balance(s.block.coinbase)
            print "Buy complete sets gas use"
            print gas_use(s)
            if(a==2):
                sellin = c.sell(ONE, int(.01*ONE), market[2], 3)
                assert(c.cancel(sellin)==1)
            assert(c.sellCompleteSets(market[a], 8*ONE)==1)
            assert(c.balance(s.block.coinbase)==(100000*ONE - 2*cumScale[a]))
            assert(c.balance(market[a])==2*cumScale[a])
            print "Sell complete sets gas use"
            print gas_use(s)
            print "market vol"
            assert(c.getVolume(market[a])==18*c.getMarketNumOutcomes(market[a])*ONE)
            assert(c.getSharesValue(market[a])==c.getCumScale(market[a])*2)
            assert(c.getTotalSharesPurchased(market[a])==2*c.getMarketNumOutcomes(market[a])*ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==TWO)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==TWO)
            assert(c.getSharesPurchased(market[a], 1)==TWO)
            assert(c.getSharesPurchased(market[a], 2)==TWO)
            # get cash balance before and after, ask is just fee
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            gas_use(s)
            sell = c.sell(ONE, int(.01*ONE), market[a], 1)
            print "selling gas use"
            print gas_use(s)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==TWO)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(len(c.get_trade_ids(market[a]))==1)
            print makerFee
            print before-after
            assert(isclose((before-after)/ONE, makerFee/ONE, rel_tol=1e-8))
            assert(isclose((afterm-beforem)/ONE, makerFee/ONE, rel_tol=1e-8))
            gas_use(s)
            c.cancel(sell)
            print "Cancel gas use"
            print gas_use(s)
            afterm = c.balance(market[a])
            after = c.balance(s.block.coinbase)
            assert(nearly_equal((before-after), 0))
            assert(nearly_equal((beforem-afterm), 0))
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==TWO)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==TWO)
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            sell = c.sell(ONE, int(.01*ONE), market[a], 1)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==TWO)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/ONE, makerFee/ONE, rel_tol=1e-8))
            assert(isclose((afterm-beforem)/ONE, makerFee/ONE, rel_tol=1e-8))
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            gas_use(s)
            # get cash balance before and after, bid includes cost + fee
            buy = c.buy(ONE, int(.01*ONE), market[a], 2)
            print "Buy gas use"
            gas_use(s)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/ONE, (makerFee + ONE*.01)/ONE, rel_tol=1e-8))
            assert(isclose((afterm-beforem)/ONE, (makerFee + ONE*.01)/ONE, rel_tol=1e-8))
            assert(len(c.get_trade_ids(market[a]))==2)
            # make sure got cost + fee back
            c.cancel(buy)
            afterm = c.balance(market[a])
            after = c.balance(s.block.coinbase)
            assert(nearly_equal((before-after), 0))
            assert(nearly_equal((beforem-afterm), 0))
            before = c.balance(s.block.coinbase)
            beforem = c.balance(market[a])
            buy = c.buy(ONE, int(.01*ONE), market[a], 2)
            after = c.balance(s.block.coinbase)
            afterm = c.balance(market[a])
            assert(isclose((before-after)/ONE, (makerFee + ONE*.01)/ONE, rel_tol=1e-8))
            assert(isclose((afterm-beforem)/ONE, (makerFee + ONE*.01)/ONE))
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==TWO)
            hash = c.makeTradeHash(0, ONE, [buy], sender=t.k2)
            c.commitTrade(hash, buy, sender=t.k2)
            s.mine(1)
            c.buyCompleteSets(market[a], 10*ONE, sender=t.k2)
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 1)==10*ONE)
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 2)==10*ONE)

            before = c.balance(sender2)
            beforem = c.balance(market[a])
            # make sure buyer got their shares, make sure seller or k2 got cash & got rid of their shares
            gas_use(s)
            x = c.trade(0, ONE, [buy], sender=t.k2)
            print "Trade gas use"
            gas_use(s)
            assert(x[2]==0)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            assert(isclose((after-before)/ONE, (ONE*.01-fee*(1+((HALF-c.getMakerFees(market[a]))/ONE)))/ONE))
            assert(isclose((beforem-afterm)/ONE, (ONE*.01+makerFee)/ONE))
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 1)==10*ONE)
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 2)==9*ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==3*ONE)
            hash = c.makeTradeHash(ONE, 0, [sell], sender=t.k2)
            c.commitTrade(hash, sell, sender=t.k2)
            s.mine(1)
            # make sure buyer or k2 got their shares and gets rid of cash, make sure seller got cash & got rid of their shares
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 1)==10*ONE)
            assert(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 2)==9*ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)==ONE)
            assert(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)==3*ONE)
            before = c.balance(sender2)
            beforem = c.balance(market[a])
            beforeog = c.balance(s.block.coinbase)
            gas_use(s)
            assert(c.trade(ONE, 0, [sell], sender=t.k2)[0]==1)
            print "Trade gas use"
            gas_use(s)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            afterog = c.balance(s.block.coinbase)
            print before
            print after
            print fee
            print c.getMakerFees(market[a])
            assert(isclose((before-after)/ONE, (ONE*.01+fee*(1+((HALF-c.getMakerFees(market[a]))/ONE)))/ONE))
            print beforem
            print afterm
            print beforem - afterm
            print makerFee
            assert(isclose((beforem-afterm)/ONE, makerFee/ONE))
            # b/c this is also creator who gets part of maker fee from maker [himself] and creator fee from taker
            assert(isclose((afterog-beforeog)/ONE, (ONE*.01 + creatorFees + makerFee/2)/ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 1)*1.0, 11.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 2)*1.0, 9.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)*1.0, 1.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2)*1.0, 1.0*3*ONE))

            assert(nearly_equal(c.getTotalSharesPurchased(market[a]), 12*c.getMarketNumOutcomes(market[a])*ONE))
            assert(nearly_equal(c.getSharesValue(market[a]), c.getCumScale(market[a])*12))
            assert(isclose(c.getVolume(market[a]), (4*ONE + 28*c.getMarketNumOutcomes(market[a])*ONE)))
            assert(isclose((c.balance(1010101)-initialBranchBal)/ONE, fee*2/ONE))
            # complete sets #*cumscale or 12*cumscale
            assert(isclose(c.balance(market[a])/ONE, 12*cumScale[a]/ONE))
            buy = c.buy(ONE, int(.01*ONE), market[a], 1, sender=t.k2)
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
            hash = c.makeTradeHash(0, ONE, [buy])
            c.commitTrade(hash, buy)
            s.mine(1)
            gas_use(s)
            print "Short sell"
            print c.short_sell(buy, ONE)
            assert(isclose(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 1)*1.0, 12.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], c.getSender(sender=t.k2), 2)*1.0, 9.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 1)*1.0, 1.0*ONE))
            assert(isclose(c.getParticipantSharesPurchased(market[a], s.block.coinbase, 2), 4.0*ONE))
            print "Short sell gas use"
            gas_use(s)
            after = c.balance(sender2)
            afterm = c.balance(market[a])
            afterog = c.balance(s.block.coinbase)
            assert(isclose((afterm-beforem)/ONE, (cumScale[a]-.01*ONE - makerFee)/ONE))
            # lose cost for complete sets and branchfees, creator fees paid by you go back to you, makerfees/2 go to you, get money back from buy order you filled
            assert(isclose((beforeog-afterog)/ONE, (cumScale[a]-.01*ONE+branchFees-makerFee/2)/ONE)==1)
            assert(isclose((beforeog-afterog)/ONE, (cumScale[a]-.01*ONE+branchFees-makerFee/2)/ONE))
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
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new ok event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new mfsatrket", 184467440737095516, event2, 1, 2, 3, 0, "yayaya", value=10**19)
    event3 = c.createEvent(1010101, "new sdok event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market3 = c.createMarket(1010101, "new msatrket", 184467440737095516, event3, 1, 2, 3, 0, "yayaya", value=10**19)
    event4 = c.createEvent(1010101, "newsdf sdok event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market4 = c.createMarket(1010101, "a matrket", 184467440737095516, event4, 1, 2, 3, 0, "yayaya", value=10**19)

    # categorical
    event5 = c.createEvent(1010101, "new sdokdf event", blocktime+1, ONE, 5*ONE, 3, "ok")
    # scalar
    event6 = c.createEvent(1010101, "new sdokdf mevent", blocktime+1, -100*ONE, 200*ONE, 2, "ok")

    c.cashFaucet(sender=t.k2)
    c.cashFaucet(sender=t.k3)
    sender = c.getSender(sender=t.k2)
    sender2 = c.getSender(sender=t.k3)
    print c.buyCompleteSets(bin_market2, 10*ONE, sender=t.k2)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < (int((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.penalizeWrong(1010101, 0)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*ONE, event2, s.block.coinbase)
    report_hash3 = c.makeHash(0, 2*ONE, event3, s.block.coinbase)
    report_hash4 = c.makeHash(0, 3*HALF, event4, s.block.coinbase)
    report_hash5 = c.makeHash(0, HALF, event5, s.block.coinbase)
    report_hash6 = c.makeHash(0, 1, event6, s.block.coinbase)
    assert(c.submitReportHash(event1, report_hash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(event4, report_hash4, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(event3, report_hash3, 0)==1)
    c.submitReportHash(event5, report_hash5, 0)
    c.submitReportHash(event6, report_hash6, 0)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event2, 0, 2*ONE, ONE, value=500000000)==1), "Report submission failed"
    assert(c.submitReport(event4, 0, 3*HALF, ONE)==1), "Report submission failed"
    assert(c.submitReport(event1, 0, ONE, ONE)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    c.setUncaughtOutcome(event1, 0)
    c.setOutcome(event1, 0)
    c.send(bin_market, ONE)
    assert(c.closeMarket(1010101, bin_market)==-2), "No outcome on market yet"
    c.setUncaughtOutcome(event1, 3*HALF)
    c.setOutcome(event1, 3*HALF)
    print "OK"
    print c.closeMarket(1010101, bin_market)
    #assert(c.closeMarket(1010101, bin_market)==0), "Already resolved indeterminate market check fail"
    assert(c.closeMarket(1010101, bin_market4)==-1)
    orig = c.balance(s.block.coinbase)
    bond = c.balance(event2)
    assert(c.balance(bin_market2)==10*ONE)
    gas_use(s)
    assert(c.closeMarket(1010101, bin_market2)==1), "Close market failure"
    print "Close market binary gas use"
    gas_use(s)
    new = c.balance(s.block.coinbase)
    origK = c.balance(c.getSender(sender=t.k2))
    # get 1/2 of liquidity (50) + 42 for event bond
    assert((new - orig)==bond), "Event bond not returned properly"
    assert(c.balance(bin_market2)==10*ONE), "Should only be winning shares remaining issue"
    assert(c.balance(event2)==0)
    # ensure proceeds returned properly
    assert(c.claimProceeds(1010101, bin_market2, sender=t.k2)==1)
    newK = c.balance(c.getSender(sender=t.k2))
    assert((newK - origK)==10*ONE), "Didn't get 10 back from selling winning shares"
    assert(c.balance(bin_market2)==0), "Payouts not done successfully"
    assert(c.balance(sender)==10000*ONE)
    # todo check winning outcomes
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
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, 2*ONE, 2, "www.roflcopter.com")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, ONE, 2*ONE, 2, "buddyholly.com")
    bin_market2 = c.createMarket(1010101, "new madrket", 184467440737095516, event2, 1, 2, 3, 0, "yayaya", value=10**19)
    event3 = c.createEvent(1010101, "new eventt3", blocktime+1, ONE, 2*ONE, 5, "buddyholly.com")
    event4 = c.createEvent(1010101, "new eventt4", blocktime+1, 0, 250*ONE, 2, "buddyholly.com")
    catmarket = c.createMarket(1010101, "newsd madrket", 184467440737095516, event3, 1, 2, 3, 0, "yayaya", value=10**19)
    scalarmarket = c.createMarket(1010101, "nescw madrket", 184467440737095516, event4, 1, 2, 3, 0, "yayaya", value=10**19)
    s.mine(1)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < int((blocktime+1)/c.getPeriodLength(1010101)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    gas_use(s)
    report_hash2 = c.makeHash(0, 2*ONE, event2, s.block.coinbase)
    report_hash3 = c.makeHash(0, HALF+1, event3, s.block.coinbase)
    report_hash4 = c.makeHash(0, int(50*ONE/250), event4, s.block.coinbase)
    gas_use(s)
    c.penalizeWrong(1010101, 0)
    assert(c.submitReportHash(event1, report_hash, 0)==1), "Report hash submission failed"
    print "hash submit gas use"
    gas_use(s)
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    print "hash submit gas use"
    assert(c.submitReportHash(event3, report_hash3, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(event4, report_hash4, 0)==1), "Report hash submission failed"
    gas_use(s)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, ONE, ONE, value=500000000)==1), "Report submission failed"
    print "report submit gas use"
    gas_use(s)
    assert(c.submitReport(event2, 0, 2*ONE, ONE)==1), "Report submission failed"
    print "report submit gas use"
    gas_use(s)
    assert(c.submitReport(event3, 0, HALF+1, ONE)==1), "Report submission failed"
    assert(c.submitReport(event4, 0, int(50*ONE/250), ONE)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = int((blocktime+1)/c.getPeriodLength(1010101))
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*ONE)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*ONE)
    gas_use(s)
    print "Not enough reports penalization gas cost"
    gas_use(s)
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*ONE)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.getTotalRep(branch)==47*ONE)
    # need to resolve event first
    c.send(bin_market, 5*ONE)
    c.send(bin_market2, 5*ONE)
    c.send(catmarket, 5*ONE)
    c.send(scalarmarket, 5*ONE)
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
    assert(c.closeMarket(1010101, catmarket)==1)
    assert(c.closeMarket(1010101, scalarmarket)==1)
    print "close market gas use"
    gas_use(s)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    gas_use(s)
    assert(c.penalizeWrong(1010101, event1)==1)
    print "Penalize wrong gas cost"
    gas_use(s)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.penalizeWrong(1010101, event3)==1)
    assert(c.penalizeWrong(1010101, event4)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101, s.block.coinbase)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "Test consensus OK"

def test_consensus_multiple_reporters():
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    c.reputationFaucet(1010101, sender=t.k2)
    c.reputationFaucet(1010101, sender=t.k3)
    c.cashFaucet(sender=t.k2)
    c.cashFaucet(sender=t.k3)
    blocktime = s.block.timestamp
    bevent = c.createEvent(1010101, "new event", blocktime+1, ONE, 2*ONE, 2, "www.roflcopter.com")
    bunethicalevent = c.createEvent(1010101, "new eventt", blocktime+1, ONE, 2*ONE, 2, "buddyholly.com")
    bindeterminateevent = c.createEvent(1010101, "new sdsdaeventt", blocktime+1, ONE, 2*ONE, 2, "buddyholly.com")
    cevent = c.createEvent(1010101, "new eventt3", blocktime+1, ONE, 2*ONE, 5, "buddyholly.com")
    sevent = c.createEvent(1010101, "new eventt4", blocktime+1, 0, 250*ONE, 2, "buddyholly.com")
    cunethicalevent = c.createEvent(1010101, "afunew eventt3", blocktime+1, ONE, 2*ONE, 5, "buddyholly.com")
    sunethicalevent = c.createEvent(1010101, "afafdsnew eventt4", blocktime+1, 0, 250*ONE, 2, "buddyholly.com")
    cindeterminateevent = c.createEvent(1010101, "sssnew evgentt3", blocktime+1, ONE, 2*ONE, 5, "buddyholly.com")
    sindeterminateevent = c.createEvent(1010101, "aanewg eventt4", blocktime+1, 0, 250*ONE, 2, "buddyholly.com")
    
    binmarket = c.createMarket(1010101, "new market", 184467440737095516, bevent, 1, 2, 3, 0, "yayaya", value=10**19)
    binmarketunethical = c.createMarket(1010101, "new madrket", 184467440737095516, bunethicalevent, 1, 2, 3, 0, "yayaya", value=10**19)
    binmarketindeterminate = c.createMarket(1010101, "new amadrket", 184467440737095516, bindeterminateevent, 1, 2, 3, 0, "yayaya", value=10**19)
    catmarket = c.createMarket(1010101, "newsd madrket", 184467440737095516, cevent, 1, 2, 3, 0, "yayaya", value=10**19)
    scalarmarket = c.createMarket(1010101, "nescw madrket", 184467440737095516, sevent, 1, 2, 3, 0, "yayaya", value=10**19)
    catmarketunethical = c.createMarket(1010101, "newsdsfs madrggket", 184467440737095516, cunethicalevent, 1, 2, 3, 0, "yayaya", value=10**19)
    scalarmarketunethical = c.createMarket(1010101, "nescwsfss madrket", 184467440737095516, sunethicalevent, 1, 2, 3, 0, "yayaya", value=10**19)
    catmarketindeterminate = c.createMarket(1010101, "newsd mabasdrket", 184467440737095516, cindeterminateevent, 1, 2, 3, 0, "yayaya", value=10**19)
    scalarmarketindeterminate = c.createMarket(1010101, "aaaaaanewrscw madrket", 184467440737095516, sindeterminateevent, 1, 2, 3, 0, "yayaya", value=10**19)
    s.mine(1)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < int((blocktime+1)/c.getPeriodLength(1010101)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    binaryeventhash = c.makeHash(0, ONE, bevent, s.block.coinbase)
    binaryeventhash2 = c.makeHash(0, 3*HALF, bevent, c.getSender(sender=t.k2))
    binaryeventhash3 = c.makeHash(0, ONE, bevent, c.getSender(sender=t.k3))
    
    binaryunethicaleventhash = c.makeHash(0, ONE, bunethicalevent, s.block.coinbase)
    binaryunethicaleventhash2 = c.makeHash(0, TWO, bunethicalevent, c.getSender(sender=t.k2))
    binaryunethicaleventhash3 = c.makeHash(0, TWO, bunethicalevent, c.getSender(sender=t.k3))
    
    binindeterminateeventhash = c.makeHash(0, 3*HALF, bindeterminateevent, s.block.coinbase)
    binindeterminateeventhash2 = c.makeHash(0, 3*HALF, bindeterminateevent, c.getSender(sender=t.k2))
    binindeterminateeventhash3 = c.makeHash(0, 3*HALF, bindeterminateevent, c.getSender(sender=t.k3))
    
    cateventhash = c.makeHash(0, 2**62, cevent, s.block.coinbase)
    cateventhash2 = c.makeHash(0, ONE, cevent, c.getSender(sender=t.k2))
    cateventhash3 = c.makeHash(0, ONE, cevent, c.getSender(sender=t.k3))
    
    cateventunethicalhash = c.makeHash(0, 1, cunethicalevent, s.block.coinbase)
    cateventunethicalhash2 = c.makeHash(0, 1, cunethicalevent, c.getSender(sender=t.k2))
    cateventunethicalhash3 = c.makeHash(0, ONE, cunethicalevent, c.getSender(sender=t.k3))
    
    cateventindeterminatehash = c.makeHash(0, HALF, cindeterminateevent, s.block.coinbase)
    cateventindeterminatehash2 = c.makeHash(0, HALF, cindeterminateevent, c.getSender(sender=t.k2))
    cateventindeterminatehash3 = c.makeHash(0, 1, cindeterminateevent, c.getSender(sender=t.k3))
    
    scalareventhash = c.makeHash(0, ONE, sevent, s.block.coinbase)
    scalareventhash2 = c.makeHash(0, 1, sevent, c.getSender(sender=t.k2))
    scalareventhash3 = c.makeHash(0, ONE, sevent, c.getSender(sender=t.k3))
    
    scalareventunethicalhash = c.makeHash(0, 1, sunethicalevent, s.block.coinbase)
    scalareventunethicalhash2 = c.makeHash(0, 1, sunethicalevent, c.getSender(sender=t.k2))
    scalareventunethicalhash3 = c.makeHash(0, 1, sunethicalevent, c.getSender(sender=t.k3))
    
    scalareventindeterminatehash = c.makeHash(0, HALF, sindeterminateevent, s.block.coinbase)
    scalareventindeterminatehash2 = c.makeHash(0, HALF, sindeterminateevent, c.getSender(sender=t.k2))
    scalareventindeterminatehash3 = c.makeHash(0, HALF, sindeterminateevent, c.getSender(sender=t.k3))
    
    c.penalizeWrong(1010101, 0)
    c.penalizeWrong(1010101, 0, sender=t.k2)
    c.penalizeWrong(1010101, 0, sender=t.k3)
    assert(c.submitReportHash(bevent, binaryeventhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(bunethicalevent, binaryunethicaleventhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(bindeterminateevent, binindeterminateeventhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(cevent, cateventhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(cunethicalevent, cateventunethicalhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(cindeterminateevent, cateventindeterminatehash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(sevent, scalareventhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(sunethicalevent, scalareventunethicalhash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(sindeterminateevent, scalareventindeterminatehash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(bevent, binaryeventhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(bunethicalevent, binaryunethicaleventhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(bindeterminateevent, binindeterminateeventhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(cevent, cateventhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(cunethicalevent, cateventunethicalhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(cindeterminateevent, cateventindeterminatehash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(sevent, scalareventhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(sunethicalevent, scalareventunethicalhash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(sindeterminateevent, scalareventindeterminatehash2, 0, sender=t.k2)==1), "Report hash submission failed"
    assert(c.submitReportHash(bevent, binaryeventhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(bunethicalevent, binaryunethicaleventhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(bindeterminateevent, binindeterminateeventhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(cevent, cateventhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(cunethicalevent, cateventunethicalhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(cindeterminateevent, cateventindeterminatehash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(sevent, scalareventhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(sunethicalevent, scalareventunethicalhash3, 0, sender=t.k3)==1), "Report hash submission failed"
    assert(c.submitReportHash(sindeterminateevent, scalareventindeterminatehash3, 0, sender=t.k3)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(bevent, 0, ONE, ONE, value=500000000)==1), "Report submission failed"
    assert(c.submitReport(bunethicalevent, 0, ONE, 0)==1), "Report submission failed"
    assert(c.submitReport(bindeterminateevent, 0, 3*HALF, ONE)==1), "Report submission failed"
    assert(c.submitReport(cevent, 0, 2**62, ONE)==1), "Report submission failed"
    assert(c.submitReport(cunethicalevent, 0, 1, 0)==1), "Report submission failed"
    assert(c.submitReport(cindeterminateevent, 0, HALF, ONE)==1), "Report submission failed"
    assert(c.submitReport(sevent, 0, ONE, ONE)==1), "Report submission failed"
    assert(c.submitReport(sunethicalevent, 0, 1, 0)==1), "Report submission failed"
    assert(c.submitReport(sindeterminateevent, 0, HALF, ONE)==1), "Report submission failed"
    assert(c.submitReport(bevent, 0, 3*HALF, 3*HALF, value=500000000, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(bunethicalevent, 0, TWO, 0, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(bindeterminateevent, 0, 3*HALF, ONE, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(cevent, 0, ONE, ONE, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(cunethicalevent, 0, 1, 0, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(cindeterminateevent, 0, HALF, ONE, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(sevent, 0, 1, ONE, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(sunethicalevent, 0, 1, 0, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(sindeterminateevent, 0, HALF, ONE, sender=t.k2)==1), "Report submission failed"
    assert(c.submitReport(bevent, 0, ONE, ONE, value=500000000, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(bunethicalevent, 0, TWO, 0, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(bindeterminateevent, 0, 3*HALF, ONE, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(cevent, 0, ONE, ONE, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(cunethicalevent, 0, ONE, 1, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(cindeterminateevent, 0, 1, ONE, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(sevent, 0, ONE, ONE, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(sunethicalevent, 0, 1, 0, sender=t.k3)==1), "Report submission failed"
    assert(c.submitReport(sindeterminateevent, 0, HALF, ONE, sender=t.k3)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    branch = 1010101
    period = int((blocktime+1)/c.getPeriodLength(1010101))
    # need to resolve event first
    c.send(binmarket, 5*ONE)
    c.send(binmarketunethical, 5*ONE)
    c.send(binmarketindeterminate, 5*ONE)
    c.send(scalarmarket, 5*ONE)
    c.send(scalarmarketunethical, 5*ONE)
    c.send(scalarmarketindeterminate, 5*ONE)
    c.send(catmarket, 5*ONE)
    c.send(catmarketunethical, 5*ONE)
    c.send(catmarketindeterminate, 5*ONE)
    
    assert(c.closeMarket(1010101, binmarket)==1)
    assert(c.closeMarket(1010101, binmarketunethical)==1)
    assert(c.closeMarket(1010101, binmarketindeterminate)==1)
    assert(c.closeMarket(1010101, scalarmarket)==1)
    assert(c.closeMarket(1010101, scalarmarketunethical)==1)
    assert(c.closeMarket(1010101, scalarmarketindeterminate)==1)
    assert(c.closeMarket(1010101, catmarket)==1)
    assert(c.closeMarket(1010101, catmarketunethical)==1)
    assert(c.closeMarket(1010101, catmarketindeterminate)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, bevent)==1)
    # didn't lose rep
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    # should gain a bit of rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(47*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, bunethicalevent)==1)
    # lost rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(46.6*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.3*ONE))
    assert(c.penalizeWrong(1010101, bindeterminateevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(46.6*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.3*ONE))
    assert(c.penalizeWrong(1010101, cevent)==1)
    # lost rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    assert(c.penalizeWrong(1010101, cunethicalevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    assert(c.penalizeWrong(1010101, cindeterminateevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    assert(c.penalizeWrong(1010101, sevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    assert(c.penalizeWrong(1010101, sunethicalevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    assert(c.penalizeWrong(1010101, sindeterminateevent)==1)
    # same rep
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(45.9*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(45.6*ONE))
    print c.getRepBalance(branch, s.block.coinbase)
    
    assert(c.getBeforeRep(branch, period, c.getSender(sender=t.k2))==c.getRepBalance(branch, c.getSender(sender=t.k2)))
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.9*ONE))
    assert(c.penalizeWrong(1010101, bevent, sender=t.k2)==1)
    assert(c.getBeforeRep(branch, period, c.getSender(sender=t.k2))==c.getRepBalance(branch, c.getSender(sender=t.k2)))
    # lose a bit of rep on 1st event
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(46.8*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.5*ONE))
    assert(c.penalizeWrong(1010101, bunethicalevent, sender=t.k2)==1)
    # gain rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.8*ONE))
    assert(c.penalizeWrong(1010101, bindeterminateevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.8*ONE))
    assert(c.penalizeWrong(1010101, cevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.8*ONE))
    assert(c.penalizeWrong(1010101, cunethicalevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.8*ONE))
    assert(c.penalizeWrong(1010101, cindeterminateevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(47.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(46.8*ONE))
    assert(c.penalizeWrong(1010101, sevent, sender=t.k2)==1)
    # lost rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(46.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(45.9*ONE))
    assert(c.penalizeWrong(1010101, sunethicalevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(46.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(45.9*ONE))
    assert(c.penalizeWrong(1010101, sindeterminateevent, sender=t.k2)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k2)) < int(46.2*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k2)) > int(45.9*ONE))
    print c.getRepBalance(branch, c.getSender(sender=t.k2))
    
    assert(c.getBeforeRep(branch, period, c.getSender(sender=t.k3))==c.getRepBalance(branch, c.getSender(sender=t.k3)))
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(47.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(46.9*ONE))
    assert(c.penalizeWrong(1010101, bevent, sender=t.k3)==1)
    assert(c.getBeforeRep(branch, period, c.getSender(sender=t.k3))==c.getRepBalance(branch, c.getSender(sender=t.k3)))
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(47.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(47*ONE))
    assert(c.penalizeWrong(1010101, bunethicalevent, sender=t.k3)==1)
    # gain rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(47.5*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(47.2*ONE))
    assert(c.penalizeWrong(1010101, bindeterminateevent, sender=t.k3)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(47.5*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(47.2*ONE))
    assert(c.penalizeWrong(1010101, cevent, sender=t.k3)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(47.5*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(47.2*ONE))
    assert(c.penalizeWrong(1010101, cunethicalevent, sender=t.k3)==1)
    # lost rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(46.6*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(46.2*ONE))
    assert(c.penalizeWrong(1010101, cindeterminateevent, sender=t.k3)==1)
    # lost rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(46.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(45.8*ONE))
    assert(c.penalizeWrong(1010101, sevent, sender=t.k3)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(46.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(45.8*ONE))
    assert(c.penalizeWrong(1010101, sunethicalevent, sender=t.k3)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(46.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(45.8*ONE))
    assert(c.penalizeWrong(1010101, sindeterminateevent, sender=t.k3)==1)
    # same rep
    assert(c.getAfterRep(branch, period, c.getSender(sender=t.k3)) < int(46.1*ONE) and c.getAfterRep(branch, period, c.getSender(sender=t.k3)) > int(45.8*ONE))
    print c.getRepBalance(branch, c.getSender(sender=t.k3))
    
    totalRep = c.getRepBalance(branch, c.getSender(sender=t.k3)) + c.getRepBalance(branch, c.getSender(sender=t.k2)) + c.getRepBalance(branch, s.block.coinbase) + c.getRepBalance(1010101, 1010101)
    
    assert(int(totalRep/ONE) > 140 and int(totalRep/ONE) < 142)
    
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    
    assert(c.collectFees(1010101, s.block.coinbase)==1)
    assert(c.collectFees(1010101, c.getSender(sender=t.k2))==1)
    assert(c.collectFees(1010101, c.getSender(sender=t.k3))==1)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "Test consensus multiple reporters OK"

def test_slashrep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, ONE, TWO, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new market2", 184467440737095516, event2, 1, 2, 3, 0, "ayayaya", value=10**19)
    i = c.getVotePeriod(1010101)
    while i < (int((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(1)   
        s.mine(1)
    c.penalizeWrong(1010101, 0)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*ONE, event2, s.block.coinbase)
    assert(c.submitReportHash(event1, report_hash, 0)==1)
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    c.slashRep(1010101, 0, ONE, s.block.coinbase, event1)
    s.mine(1)
    periodLength = c.getPeriodLength(1010101)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    print c.submitReport(event1, 0, ONE, ONE, value=500000000)
    #assert(c.submitReport(event1, 0, ONE, ONE, value=500000000)==1), "Report submission failed"
    assert(c.submitReport(event2, 0, 2*ONE, ONE)==1), "Report submission failed"
    s.mine(1)
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==1)
    branch = 1010101
    period = c.getVotePeriod(1010101) - 1
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    # need to resolve event first
    c.send(bin_market, ONE)
    c.send(bin_market2, ONE)
    assert(c.closeMarket(1010101, bin_market2)==1)

    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, s.block.coinbase)==int(23.5*ONE))
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, s.block.coinbase)==int(23.5*ONE))
    # other half of rep should be in branch
    assert(c.getRepBalance(branch, branch)==433498485732174462976)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101, s.block.coinbase)==1)
    assert(c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getRepBalance(branch, branch)==0)
    print "Test slashrep OK"

def test_claimrep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    c.setBeforeRep(1010101, c.getVotePeriod(1010101), 47*ONE, s.block.coinbase)
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
    assert(c.penalizationCatchup(1010101, s.block.coinbase)==1)
    diffInPeriods = i - origi
    diffInPeriods = min(diffInPeriods, 23)
    print blocktime
    print c.getVotePeriod(1010101)
    print blocktime / 15
    assert(isclose(c.getRepBalance(1010101, s.block.coinbase)/ONE, 47*.9**diffInPeriods*ONE/ONE))
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, TWO, 2, "ok")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, ONE, TWO, 2, "ok")
    bin_market2 = c.createMarket(1010101, "new market2", 184467440737095516, event2, 1, 2, 3, 0, "ayayaya", value=10**19)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 2*ONE, event2, s.block.coinbase)
    i = c.getVotePeriod(1010101)
    while i < int(((blocktime+1)/c.getPeriodLength(1010101))):
        c.incrementPeriod(1010101)
        i += 1
    periodLength = c.getPeriodLength(1010101)
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.penalizeWrong(1010101, 0)
    n = c.submitReportHash(event1, report_hash, 0)
    print n
    print s.block.timestamp
    assert(n==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, ONE, ONE, value=500000000)==1), "Report submission failed"
    assert(c.submitReport(event2, 0, 2*ONE, ONE)==1), "Report submission failed"
    c.incrementPeriod(1010101)
    branch = 1010101
    period = c.getVotePeriod(1010101)-1
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    print c.getRepBalance(branch, branch)
    assert(isclose(c.getRepBalance(branch, branch)/ONE, ((47*ONE - 47*.9**diffInPeriods*ONE)/ONE)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    print s.block.timestamp
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    print s.block.timestamp

    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(isclose(c.getRepBalance(branch, branch)/ONE, ((47*ONE - 47*.9**diffInPeriods*ONE)/ONE)))
    assert(c.getTotalRep(branch)==866996971464348925952)

    # need to resolve event first
    c.send(bin_market, ONE)
    c.send(bin_market2, ONE)
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)
    
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(isclose(c.getRepBalance(branch, branch)/ONE, ((47*ONE - 47*.9**diffInPeriods*ONE)/ONE)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.penalizeWrong(1010101, event1)==1)

    print c.getBeforeRep(branch, period, s.block.coinbase)
    assert(isclose(c.getBeforeRep(branch, period, s.block.coinbase)/ONE, 47*.9**diffInPeriods*ONE/ONE))
    assert(isclose(c.getRepBalance(branch, s.block.coinbase)/ONE, 47*.9**diffInPeriods*ONE/ONE))
    assert(isclose(c.getRepBalance(branch, branch)/ONE, ((47*ONE - 47*.9**diffInPeriods*ONE)/ONE)))
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.penalizeWrong(1010101, event2)==1)
    
    assert(isclose(c.getBeforeRep(branch, period, s.block.coinbase)/ONE, 47*.9**diffInPeriods*ONE/ONE))
    assert(isclose(c.getRepBalance(branch, s.block.coinbase)/ONE, 47*.9**diffInPeriods*ONE/ONE))
    assert(isclose(c.getRepBalance(branch, branch)/ONE, ((47*ONE - 47*.9**diffInPeriods*ONE)/ONE)))
    assert(c.getTotalRep(branch)==47*ONE)
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.collectFees(1010101, s.block.coinbase)==1)
    assert(c.getRepBalance(branch, s.block.coinbase)==866996971464348925952)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==866996971464348925952)
    print "Test catchup OK"

def test_market_pushback():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+10000, ONE, 2*ONE, 2, "www.roflcopter.com")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventa", blocktime+10000, ONE, 2*ONE, 2, "www.roflcopter.coms")
    bin_market2 = c.createMarket(1010101, "new vmarket", 184467440737095516, event2, 1, 2, 3, 0, "yayayam", value=10**19)
    c.buyCompleteSets(bin_market, TWO)
    c.buyCompleteSets(bin_market2, TWO)
    c.pushMarketForward(1010101, bin_market)
    c.pushMarketForward(1010101, bin_market2)
    periodLength = c.getPeriodLength(1010101)
    i = c.getVotePeriod(1010101)
    while i < int(s.block.timestamp/c.getPeriodLength(1010101)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 3*HALF, event2, s.block.coinbase)
    c.penalizeWrong(1010101, 0)
    print c.submitReportHash(event1, report_hash)
    print event1
    print report_hash
    assert(c.submitReportHash(event1, report_hash, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event1, 0, ONE, ONE, value=5000000000)==1), "Report submission failed"
    assert(c.submitReport(event2, 0, 3*HALF, ONE)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    branch = 1010101
    period = int((blocktime)/c.getPeriodLength(1010101))
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*ONE)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*ONE)
    gas_use(s)
    # get events in periods both old and new here
    assert(len(c.getEvents(1010101, int((blocktime+10000)/15)))==2)
    assert(len(c.getEvents(1010101, c.getVotePeriod(1010101)-1))==2)
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==-6)
    # get events in periods both old and new here again and make sure proper
    # for event 1 
    # - early expiration should exist there
    assert(c.getEvents(1010101, c.getVotePeriod(1010101)-1)[0]==event1)
    # - original further off one it shouldn't exist in
    assert(c.getEvents(1010101, int((blocktime+10000)/15))[0]==0)
    # for event 2 
    # - it should have a rejected period and be rejected
    assert(c.getRejected(event2)==1)
    assert(c.getRejectedPeriod(event2)>=1)
    # - early expiration should exist there
    assert(c.getEvents(1010101, c.getVotePeriod(1010101)-1)[1]==event2)
    # - original further off it should exist and be reported on in
    assert(c.getEvents(1010101, int((blocktime+10000)/15))[1]==event2)
    # - for event 1 should penalize on the early expiration and not be able to on the original
    # - when penalizing should "penalize" [not really get a free pass] on the rejected period and then on the real reporting period later for event 2
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event1)==1)
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    i = c.getVotePeriod(1010101)
    s.mine(1)
    while i < int((blocktime+10000)/c.getPeriodLength(1010101)):
        c.incrementPeriod(1010101)
        i += 1
    while(s.block.timestamp%c.getPeriodLength(1010101) > periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    c.penalizeWrong(1010101, event1)
    c.penalizeWrong(1010101, event2)
    report_hash = c.makeHash(0, ONE, event1, s.block.coinbase)
    report_hash2 = c.makeHash(0, 3*HALF, event2, s.block.coinbase)
    assert(c.submitReportHash(event1, report_hash, 0)==-1), "Report hash -1 check failed"
    assert(c.submitReportHash(event2, report_hash2, 0)==1), "Report hash submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    assert(c.submitReport(event2, 0, 3*HALF, ONE, value=5000000000)==1), "Report submission failed"
    while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
        time.sleep(c.getPeriodLength(1010101)/2)
        s.mine(1)
    c.incrementPeriod(1010101)
    branch = 1010101
    period = c.getVotePeriod(1010101) - 1
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*ONE)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*ONE)
    gas_use(s)
    # get events in periods both old and new here
    assert(c.getEvents(1010101, c.getVotePeriod(1010101)-1)[1]==event2)
    assert(c.closeMarket(1010101, bin_market2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(48*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getAfterRep(branch, period, s.block.coinbase) < int(48*ONE) and c.getAfterRep(branch, period, s.block.coinbase) > int(46*ONE))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    
    while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
        time.sleep(int(periodLength/2))
        s.mine(1)
    
    assert(c.collectFees(1010101, s.block.coinbase)==1)
    assert(c.getRepBalance(branch, s.block.coinbase)==47*ONE)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*ONE)
    print "Test push back OK"
    
def test_pen_not_enough_reports():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, 2*ONE, 2, "www.roflcopter.com")
    bin_market = c.createMarket(1010101, "new market", 184467440737095516, event1, 1, 2, 3, 0, "yayaya", value=10**19)
    event2 = c.createEvent(1010101, "new eventt", blocktime+1, ONE, 2*ONE, 2, "buddyholly.com")
    bin_market2 = c.createMarket(1010101, "new madrket", 184467440737095516, event2, 1, 2, 3, 0, "yayaya", value=10**19)
    c.buyCompleteSets(bin_market, TWO)
    c.buyCompleteSets(bin_market2, TWO)
    c.incrementPeriod(1010101)
    c.setNumEventsToReportOn(branch)
    c.calculateReportTargetForEvent(1010101, event1, c.getVotePeriod(1010101), s.block.coinbase)
    c.calculateReportTargetForEvent(1010101, event2, c.getVotePeriod(1010101), s.block.coinbase)
    c.incrementPeriod(1010101)
    c.proveReporterDidntReportEnough(1010101, s.block.coinbase, event1, sender=t.k2)
    print "Test penalize not enough OK"

def test_update_trading_fee():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    # do the state-modifications have to be in the Serpent code...?
    # CASH = s.abi_contract('../local/data_api/cash.se')
    # MARKETS = s.abi_contract('../local/data_api/markets.se')
    # FAUCETS = s.abi_contract('../local/functions/faucets.se')
    # CREATEMARKET = s.abi_contract('../local/functions/createMarket.se')
    # CASH.initiateOwner(1010101)
    # FAUCETS.reputationFaucet(1010101)
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    blocktime = s.block.timestamp
    # event1 = CREATEMARKET.createEvent(1010101, "new event", blocktime+1, ONE, 2*ONE, 2, "www.roflcopter.com")
    event1 = c.createEvent(1010101, "new event", blocktime+1, ONE, 2*ONE, 2, "www.roflcopter.com")
    tradingFee = 120000000000000000  #.12
    makerFee = 250000000000000000  #.25
    # market = CREATEMARKET.createMarket(1010101, "new market", tradingFee, event1, 1, 2, 3, makerFee, "yayaya", value=10**19)
    market = c.createMarket(1010101, "new market", tradingFee, event1, 1, 2, 3, makerFee, "yayaya", value=10**19)
    tradingFee = 110000000000000000 #.11
    makerFee = 220000000000000000 #.22
    #test valid tradingFees
    # result = CREATEMARKET.updateTradingFee(1010101, market, tradingFee, makerFee);
    result = c.updateTradingFee(1010101, market, tradingFee, makerFee);
    assert(result == 1);
    # assert(MARKETS.getTradingFee(market) == tradingFee)
    # assert(MARKETS.getMakerFees(market) == makerFee);
    assert(c.getTradingFee(market) == tradingFee)
    assert(c.getMakerFees(market) == makerFee);
    #the fees are too damn high
    tradingFee = 120000000000000000  #.12
    # result = CREATEMARKET.updateTradingFee(1010101, market, tradingFee, makerFee);
    result = c.updateTradingFee(1010101, market, tradingFee, makerFee);
    assert(result == -2);
    # assert(MARKETS.getTradingFee(market) != tradingFee)
    assert(c.getTradingFee(market) != tradingFee)
    tradingFee = 100000000000000000  #.10
    makerFee = 510000000000000000  #.51
    # result = CREATEMARKET.updateTradingFee(1010101, market, tradingFee, makerFee);
    result = c.updateTradingFee(1010101, market, tradingFee, makerFee);
    assert(result == -2);
    # assert(MARKETS.getMakerFees(market) != makerFee)
    assert(c.getMakerFees(market) != makerFee)
    print "Test update trading fees ok"

# calculate the maximum number of ask trade_ids in a single trade
def calculate_max_asks(s, c, gas_limit):
    gas_used, num_trades = 0, 0
    asks = {}
    while gas_used < gas_limit:
        num_trades += 1
        event1 = c.createEvent(1010101, "new event", s.block.timestamp+1, ONE, 2*ONE, 2, "lmgtfy.com")
        market = c.createMarket(1010101, "new market", 120000000000000000, event1, 1, 2, 3, 250000000000000000, "best market ever", value=10**19)
        assert(c.setCash(s.block.coinbase, 10000000000*ONE) == 1)
        assert(c.setCash(c.getSender(sender=t.k2), 10000000000*ONE) == 1)
        s.mine(1)
        qty = num_trades*ONE
        c.buyCompleteSets(market, qty)
        [c.sell(ONE, int(.01*i*ONE), market, 1) for i in range(num_trades + 1)]
        trades = c.get_trade_ids(market)
        assert(len(trades) == num_trades)
        assert(c.commitTrade(c.makeTradeHash(qty, 0, trades), sender=t.k2) == 1)
        s.mine(1)
        gas_use(s)
        c.trade(qty, 0, trades, sender=t.k2)
        gas_used = gas_use(s)
        asks[num_trades] = int(gas_limit - gas_used)
        s.mine(1)
    return num_trades - 1, asks

# calculate the maximum number of bid trade_ids in a single trade
def calculate_max_bids(s, c, gas_limit):
    gas_used, num_trades = 0, 0
    bids = {}
    while gas_used < gas_limit:
        num_trades += 1
        event1 = c.createEvent(1010101, "new event", s.block.timestamp+1, ONE, 2*ONE, 2, "lmgtfy.com")
        market = c.createMarket(1010101, "new market", 120000000000000000, event1, 1, 2, 3, 250000000000000000, "best market ever", value=10**19)
        assert(c.setCash(s.block.coinbase, 10000000000*ONE) == 1)
        assert(c.setCash(c.getSender(sender=t.k2), 10000000000*ONE) == 1)
        s.mine(1)
        [c.buy(ONE, int(.01*i*ONE), market, 1) for i in range(num_trades + 1)]
        trades = c.get_trade_ids(market)
        assert(len(trades) == num_trades)
        qty = num_trades*ONE
        assert(c.commitTrade(c.makeTradeHash(0, qty, trades), sender=t.k2) == 1)
        c.buyCompleteSets(market, qty, sender=t.k2)
        s.mine(1)
        gas_use(s)
        c.trade(0, qty, trades, sender=t.k2)
        gas_used = gas_use(s)
        bids[num_trades] = int(gas_limit - gas_used)
        s.mine(1)
    return num_trades - 1, bids

# Calculate the maximum number of trade IDs allowed for a single trade:
# 1 + (gas_limit - first_tradeid_gas_cost) // next_tradeid_gas_cost
def calculate_max_trade_ids(gas_limit=3135000):
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    max_asks, asks = calculate_max_asks(s, c, gas_limit)
    max_bids, bids = calculate_max_bids(s, c, gas_limit)
    print "Max # asks: %i [%i of %i gas remaining]" % (max_asks, asks[max_asks], gas_limit)
    print "Max # bids: %i [%i of %i gas remaining]" % (max_bids, bids[max_bids], gas_limit)
    pprint(asks)
    pprint(bids)

def gas_use(s):
    global initial_gas
    print "Gas Used:"
    gas_used = s.block.gas_used - initial_gas
    print gas_used
    initial_gas = s.block.gas_used
    return gas_used

if __name__ == '__main__':
    src = os.path.join(os.getenv('AUGUR_CORE', os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace')), 'src')
    output = os.path.join(src, 'functions', 'output.se')
    if os.path.exists(output): os.remove(output)
    os.system('python mk_test_file.py \'' + os.path.join(src, 'functions') + '\' \'' + os.path.join(src, 'data_api') + '\' \'' + os.path.join(src, 'functions') + '\'')
    # data/api tests
    #test_cash()
    #test_ether()
    #test_log_exp()
    #test_exp()
    #test_markets()
    #test_reporting()

    # function tests
    #test_trading()
    #test_create_branch()
    #test_send_rep()
    #test_market_pushback()
    #test_close_market()
    #test_consensus()
    #test_catchup()
    #test_slashrep()
    #test_claimrep()
    #test_consensus_multiple_reporters()
    #test_pen_not_enough_reports()
    #test_update_trading_fee()
    calculate_max_trade_ids(gas_limit=4712388)
    print "DONE TESTING"

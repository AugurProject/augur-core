// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/ReputationToken.sol';
import 'ROOT/reporting/DisputeBondToken.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/ERC20Basic.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';


contract Market is DelegationTarget, Typed, Initializable {
    using SafeMathUint256 for uint256;

    // CONSIDER: change the payoutNumerator/payoutDenominator to use fixed point numbers instead of integers; PRO: some people find fixed point decimal values easier to grok; CON: rounding errors can occur and it is easier to screw up the math if you don't handle fixed point values correctly
    int256 private payoutDenominator;
    uint256 private feePerEthInAttoeth;

    // CONSIDER: we really don't need these
    int256 private maxDisplayPrice;
    int256 private minDisplayPrice;

    // CONSIDER: figure out approprate values for these
    private constant uint256 AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20;
    private constant uint256 LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21;
    private constant uint256 ALL_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22;

    ReportingWindow private reportingWindow;
    uint256 private endTime;
    uint256 private numOutcomes;
    uint256 private marketCreationBlock;
    ITopic private topic;
    address private automatedReporterAddress;
    ReportingToken[] private reportingTokens;
    Cash private denominationToken;
    address private creator;
    IShareToken[] private shareTokens;
    uint256 private finalizationTime;
    bool private automatedReportReceived;
    bytes32 private tentativeWinningPayoutDistributionHash;
    bytes32 private finalPayoutDistributionHash;
    DisputeBondToken private automatedReporterDisputeBondToken;
    DisputeBondToken private limitedReportersDisputeBondToken;
    DisputeBondToken private allReportersDisputeBondToken;
    uint256 private validityBondAttoeth;
    uint256 private automatedReporterBondAttoeth;

    def initialize(reportingWindow: address, endTime: uint256, numOutcomes: uint256, payoutDenominator: int256, feePerEthInAttoeth: uint256, denominationToken: address, creator: address, minDisplayPrice: int256, maxDisplayPrice: int256, automatedReporterAddress: address, topic: ITopic):
        require(not initialized)
        initialized = 1
        require(reportingWindow)
        require(2 <= payoutDenominator and payoutDenominator <= 2**254)
        require(2 <= numOutcomes and numOutcomes <= 8)
        // payoutDenominator must be a multiple of numOutcomes so we can evenly split complete set share payout on indeterminate
        require(not (payoutDenominator % numOutcomes))
        require(0 <= feePerEthInAttoeth and feePerEthInAttoeth <= 5*10**17)
        require(-2**254 <= maxDisplayPrice and maxDisplayPrice <= 2**254)
        require(-2**254 <= minDisplayPrice and minDisplayPrice <= 2**254)
        completeSetCostMultiplier = maxDisplayPrice - minDisplayPrice
        require(1 <= completeSetCostMultiplier and completeSetCostMultiplier <= 2**254)
        require(creator)
        // FIXME: require market to be on a non-forking branch; repeat this check up the stack as well if necessary (e.g., in reporting window)
        // CONSIDER: should we allow creator to send extra ETH, is there risk of variability in bond requirements?
        require(msg.value == MarketFeeCalculator(controller.lookup('MarketFeeCalculator')).getValidityBond(reportingWindow) + MarketFeeCalculator(controller.lookup('MarketFeeCalculator')).getTargetReporterGasCosts())
        reportingWindow = reportingWindow
        endTime = endTime
        numOutcomes = numOutcomes
        payoutDenominator = payoutDenominator
        // FIXME: markets may be denominated in tokens that aren't 10^18, deal with that
        feePerEthInAttoeth = feePerEthInAttoeth
        maxDisplayPrice = maxDisplayPrice
        minDisplayPrice = minDisplayPrice
        marketCreationBlock = block.number
        topic = topic
        automatedReporterAddress = automatedReporterAddress
        denominationToken = denominationToken
        creator = creator
        reportingTokens = MapFactory(controller.lookup('MapFactory')).createMap(controller, this)
        outcome = 0
        while(outcome < numOutcomes):
            shareTokens[outcome] = ShareTokenFactory(controller.lookup('ShareTokenFactory')).createShareToken(controller, this, outcome)
            outcome += 1
        approveSpenders()
        require(controller.lookup('Cash') == denominationToken or getBranch().isContainerForShareToken(denominationToken))
        return(1)

        // TODO: we need to update this signature (and all of the places that call it) to allow the creator (UI) to pass in a number of other things which will all be logged here
        // TODO: log short description
        // TODO: log long description
        // TODO: log min display price
        // TODO: log max display price
        // TODO: log tags (0-2)
        // TODO: log outcome labels (same number as numOutcomes)
        // TODO: log type (scalar, binary, categorical)
        // TODO: log any immutable data associated with the market (e.g., endTime, numOutcomes, payoutDenominator, denominationToken address, etc.)

    // this will need to be called manually for each open market if a spender contract is updated
    def approveSpenders():
        denominationToken.approve(controller.lookup('cancelOrder'), 2**254)
        denominationToken.approve(controller.lookup('completeSets'), 2**254)
        denominationToken.approve(controller.lookup('takeOrder'), 2**254)
        denominationToken.approve(controller.lookup('tradingEscapeHatch'), 2**254)
        denominationToken.approve(controller.lookup('claimProceeds'), 2**254)
        denominationToken.approve(controller.lookup('tradingEscapeHatch'), 2**254)
        i = 0
        while i < numOutcomes:
            shareTokens[i].approve(controller.lookup('takeOrder'), 2**254)
            i += 1
        return 1

    def changeCreator(newCreator: address):
        require(msg.sender == creator)
        creator = newCreator
        return 1

    def decreaseMarketCreatorSettlementFeeInAttoethPerEth(newFeePerEthInWei: int256):
        require(0 <= newFeePerEthInWei and newFeePerEthInWei < feePerEthInAttoeth)
        require(msg.sender == creator)
        feePerEthInAttoeth = newFeePerEthInWei
        return 1

    def automatedReport(payoutNumerators: arr):
        assertNoValue()
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(msg.sender == automatedReporterAddress)
        require(isInAutomatedReportingPhase())
        // we have to create the reporting token so the rest of the system works (winning reporting token must exist)
        getReportingToken(payoutNumerators)
        automatedReportReceived = 1
        tentativeWinningPayoutDistributionHash = derivePayoutDistributionHash(payoutNumerators)
        reportingWindow.updateMarketPhase()
        return 1

    def disputeAutomatedReport():
        assertNoValue()
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(not isFinalized())
        require(isInAutomatedDisputePhase())
        require(not automatedReporterDisputeBondToken)
        automatedReporterDisputeBondToken = DisputeBondTokenFactory(controller.lookup('DisputeBondTokenFactory')).createDisputeBondToken(controller, this, msg.sender, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash)
        fundDisputeBondWithReputation(msg.sender, automatedReporterDisputeBondToken, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT)
        reportingWindow.updateMarketPhase()
        return 1

    def disputeLimitedReporters():
        assertNoValue()
        migrateThroughAllForks()
        require(isInLimitedDisputePhase())
        limitedReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup('DisputeBondTokenFactory')).createDisputeBondToken(controller, this, msg.sender, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash)
        fundDisputeBondWithReputation(msg.sender, limitedReportersDisputeBondToken, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT)
        newReportingWindow = getBranch().getNextReportingWindow()
        newReportingWindow.migrateMarketInFromSibling()
        reportingWindow.removeMarket()
        reportingWindow = newReportingWindow
        return 1

    def disputeAllReporters():
        assertNoValue()
        migrateThroughAllForks()
        require(isInAllDisputePhase())
        require(limitedReportersDisputeBondToken)
        allReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup('DisputeBondTokenFactory')).createDisputeBondToken(controller, this, msg.sender, ALL_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash)
        fundDisputeBondWithReputation(msg.sender, allReportersDisputeBondToken, ALL_REPORTERS_DISPUTE_BOND_AMOUNT)
        reportingWindow.getBranch().fork()
        newReportingWindow = getBranch().getReportingWindowByTimestamp(getBranch().getForkEndTime())
        newReportingWindow.migrateMarketInFromSibling()
        reportingWindow.removeMarket()
        reportingWindow = newReportingWindow
        return 1

    def updateTentativeWinningPayoutDistributionHash(payoutDistributionHash: bytes32):
        assertNoValue()
        require(reportingTokens.contains(payoutDistributionHash))
        if (not tentativeWinningPayoutDistributionHash):
            tentativeWinningPayoutDistributionHash = payoutDistributionHash
        // FIXME: I believe we can just keep the if block below and remove one above.
        // Check to make sure, but I'm pretty confident that if you do
        // reportingTokens.contains(0) you will get back 0.
        if not reportingTokens.contains(tentativeWinningPayoutDistributionHash):
            tentativeWinningPayoutDistributionHash = payoutDistributionHash
        if (reportingTokens.getValue(payoutDistributionHash).totalSupply() > reportingTokens.getValue(tentativeWinningPayoutDistributionHash).totalSupply()):
            tentativeWinningPayoutDistributionHash = payoutDistributionHash
        return 1

    def tryFinalize():
        assertNoValue()
        tryFinalizeAutomatedReport()
        if (isFinalized()):
            return(1)
        tryFinalizeLimitedReporting()
        if (isFinalized()):
            return(1)
        tryFinalizeAllReporting()
        if (isFinalized()):
            return(1)
        tryFinalizeFork()
        if (isFinalized()):
            return(1)
        return(0)

        // FIXME: when the market is finalized, we need to add `reportingTokens[finalPayoutDistributionHash].totalSupply()` to the reporting window.  This is necessary for fee collection which is a cross-market operation.
        // TODO: figure out how to make it so fee distribution is delayed until all markets have been finalized; we can enforce it contract side and let the UI deal with the actual work
        // FIXME: if finalPayoutDistributionHash != getIdentityDistributionId(), pay back validity bond holder
        // FIXME: if finalPayoutDistributionHash == getIdentityDistributionId(), transfer validity bond to reportingWindow (reporter fee pot)
        // FIXME: if automated report is wrong, transfer automated report bond to reportingWindow
        // FIXME: if automated report is right, transfer automated report bond to market creator
        // FIXME: handle markets that get 0 reports during their scheduled reporting window

    def tryFinalizeAutomatedReport():
        assertNoValue()
        if (isFinalized()):
            return(1)
        if (not automatedReportReceived):
            return(0)
        if (automatedReporterDisputeBondToken):
            return(0)
        if (block.timestamp < getAutomatedReportDisputeDueTimestamp()):
            return(0)
        require(tentativeWinningPayoutDistributionHash)
        finalPayoutDistributionHash = tentativeWinningPayoutDistributionHash
        finalizationTime = block.timestamp
        transferIncorrectDisputeBondsToWinningReportingToken()
        reportingWindow.updateMarketPhase()
        return(1)

    def tryFinalizeLimitedReporting():
        assertNoValue()
        migrateThroughAllForks()
        if (isFinalized()):
            return(1)
        if (limitedReportersDisputeBondToken):
            return(0)
        if (block.timestamp <= reportingWindow.getEndTime()):
            return(0)
        finalPayoutDistributionHash = tentativeWinningPayoutDistributionHash
        finalizationTime = block.timestamp
        transferIncorrectDisputeBondsToWinningReportingToken()
        reportingWindow.updateMarketPhase()
        return(1)

    def tryFinalizeAllReporting():
        assertNoValue()
        migrateThroughAllForks()
        if (isFinalized()):
            return(1)
        if (not limitedReportersDisputeBondToken):
            return(0)
        if (allReportersDisputeBondToken):
            return(0)
        if (block.timestamp <= reportingWindow.getEndTime()):
            return(0)
        finalPayoutDistributionHash = tentativeWinningPayoutDistributionHash
        finalizationTime = block.timestamp
        transferIncorrectDisputeBondsToWinningReportingToken()
        reportingWindow.updateMarketPhase()
        return(1)

    def tryFinalizeFork():
        assertNoValue()
        if (isFinalized()):
            return(1)
        if (not limitedReportersDisputeBondToken):
            return(0)
        if (not allReportersDisputeBondToken):
            return(0)
        if (reportingWindow.getBranch().getForkingMarket() != this):
            return(0)
        winningDestination = getReputationToken().getTopMigrationDestination()
        if (not winningDestination):
            return(0)
        if (winningDestination.totalSupply() < 11 * 10**6 * 10**18 / 2 and block.timestamp < getBranch().getForkEndTime()):
            return(0)
        finalPayoutDistributionHash = winningDestination.getBranch().getParentPayoutDistributionHash()
        finalizationTime = block.timestamp
        transferIncorrectDisputeBondsToWinningReportingToken()
        reportingWindow.updateMarketPhase()
        return(1)

    def migrateThroughAllForks():
        assertNoValue()
        // this will loop until we run out of gas, follow forks until there are no more, or have reached an active fork (which will throw)
        while (migrateThroughOneFork()):
            noop = 1
        return 1

    // returns 0 if no move occurs, 1 if move occurred, throws if a fork not yet resolved
    def migrateThroughOneFork():
        assertNoValue()
        if (isFinalized()):
            return(1)
        if (not needsMigration()):
            return(0)
        // only proceed if the forking market is finalized
        require(reportingWindow.getBranch().getForkingMarket().isFinalized())
        if (limitedReportersDisputeBondToken):
            limitedReportersDisputeBondToken = 0
        if (allReportersDisputeBondToken):
            allReportersDisputeBondToken = 0
        currentBranch = getBranch()
        // follow the forking market to its branch and then attach to the next reporting window on that branch
        winningForkPayoutDistributionHash = currentBranch.getForkingMarket().getFinalPayoutDistributionHash()
        destinationBranch = currentBranch.getChildBranch(winningForkPayoutDistributionHash)
        newReportingWindow = destinationBranch.getNextReportingWindow()
        newReportingWindow.migrateMarketInFromNibling()
        reportingWindow.removeMarket()
        reportingWindow = newReportingWindow
        // reset to unreported state
        limitedReportersDisputeBondToken = 0
        allReportersDisputeBondToken = 0
        tentativeWinningPayoutDistributionHash = 0
        reportingTokens = MapFactory(controller.lookup('MapFactory')).createMap(controller, this)
        return(1)


    ////////
    //////// Helpers
    ////////

    def getReportingToken(payoutNumerators: arr):
        assertNoValue()
        payoutDistributionHash = derivePayoutDistributionHash(payoutNumerators)
        if (not reportingTokens.contains(payoutDistributionHash)):
            reportingTokens.addMapItem(payoutDistributionHash, ReportingTokenFactory(controller.lookup('ReportingTokenFactory')).createReportingToken(controller, this, payoutNumerators))
        return(reportingTokens.getValue(payoutDistributionHash): address)

    def getReportingTokenOrZeroByPayoutDistributionHash(payoutDistributionHash: bytes32):
        assertNoValue()
        return(reportingTokens.getValueOrZero(payoutDistributionHash))

    def derivePayoutDistributionHash(payoutNumerators: arr):
        assertNoValue()
        validatePayoutNumerators(payoutNumerators)
        return(sha3(payoutNumerators, items = len(payoutNumerators)): bytes32)

    def validatePayoutNumerators(payoutNumerators: arr):
        assertNoValue()
        i = 0
        sum = 0
        require(len(payoutNumerators) == numOutcomes)
        while (i < numOutcomes):
            require(0 <= payoutNumerators[i] and payoutNumerators[i] <= payoutDenominator)
            sum += payoutNumerators[i]
            i += 1
        require(sum == payoutDenominator)
        return 1

    def fundDisputeBondWithReputation(bondHolder: address, disputeBondToken: address, bondAmount: uint256):
        assertPrivateCall()
        require(bondHolder == disputeBondToken.getBondHolder())
        reputationToken = getReputationToken()
        reputationToken.trustedTransfer(bondHolder, disputeBondToken, bondAmount)
        return 1

    def transferIncorrectDisputeBondsToWinningReportingToken():
        assertPrivateCall()
        require(isFinalized())
        reputationToken = getReputationToken()
        if (getBranch().getForkingMarket() == this):
            return 1
        if (automatedReporterDisputeBondToken and automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() == finalPayoutDistributionHash):
            reputationToken.trustedTransfer(automatedReporterDisputeBondToken, getFinalWinningReportingToken(), reputationToken.balanceOf(automatedReporterDisputeBondToken))
        if (limitedReportersDisputeBondToken and limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() == finalPayoutDistributionHash):
            reputationToken.trustedTransfer(limitedReportersDisputeBondToken, getFinalWinningReportingToken(), reputationToken.balanceOf(limitedReportersDisputeBondToken))
        return 1


    ////////
    //////// Getters
    ////////

    def getTypeName():
        return "Market"

    def getReportingWindow():
        assertNoValue()
        return(reportingWindow: address)

    def getBranch():
        assertNoValue()
        return(reportingWindow.getBranch(): address)

    def getReputationToken():
        assertNoValue()
        return(reportingWindow.getReputationToken(): address)

    def getRegistrationToken():
        assertNoValue()
        return(reportingWindow.getRegistrationToken(): address)

    def getAutomatedReporterDisputeBondToken():
        assertNoValue()
        return(automatedReporterDisputeBondToken: address)

    def getLimitedReportersDisputeBondToken():
        assertNoValue()
        return(limitedReportersDisputeBondToken: address)

    def getAllReportersDisputeBondToken():
        assertNoValue()
        return(allReportersDisputeBondToken: address)

    def getNumberOfOutcomes():
        assertNoValue()
        return(numOutcomes)

    def getEndTime():
        return endTime

    def getTentativeWinningPayoutDistributionHash():
        assertNoValue()
        return(tentativeWinningPayoutDistributionHash : bytes32)

    def getFinalWinningReportingToken():
        assertNoValue()
        return(reportingTokens.getValue(finalPayoutDistributionHash): address)

    def getShareToken(outcome: int256):
        assertNoValue()
        require(0 <= outcome and outcome < numOutcomes)
        return(shareTokens[outcome]: address)

    def getFinalPayoutDistributionHash():
        assertNoValue()
        return(finalPayoutDistributionHash : bytes32)

    def getPayoutDenominator():
        assertNoValue()
        return(payoutDenominator)

    def getDenominationToken():
        assertNoValue()
        return(denominationToken: address)

    def getCreator():
        return(creator: address)

    def getMarketCreatorSettlementFeeInAttoethPerEth():
        return(feePerEthInAttoeth)

    def getMaxDisplayPrice():
        assertNoValue()
        return(maxDisplayPrice)

    def getMinDisplayPrice():
        assertNoValue()
        return(minDisplayPrice)

    def getCompleteSetCostInAttotokens():
        assertNoValue()
        return(maxDisplayPrice - minDisplayPrice)

    def getTopic():
        assertNoValue()
        return(topic)

    def shouldCollectReportingFees():
        return not getBranch().isContainerForShareToken(denominationToken)

    def isDoneWithAutomatedReporters():
        assertNoValue()
        return(automatedReportReceived or block.timestamp > getAutomatedReportDueTimestamp())

    def isDoneWithLimitedReporters():
        assertNoValue()
        if isFinalized():
            return 1
        if limitedReportersDisputeBondToken:
            return 1
        if block.timestamp > reportingWindow.getEndTime():
            return 1
        return 0

    def isDoneWithAllReporters():
        assertNoValue()
        if isFinalized():
            return 1
        if allReportersDisputeBondToken:
            return 1
        if block.timestamp > reportingWindow.getEndTime():
            return 1
        return 0

    def isFinalized():
        assertNoValue()
        return(finalPayoutDistributionHash != 0)

    def getFinalizationTime():
        return finalizationTime

    def isInAutomatedReportingPhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (block.timestamp < endTime):
            return(0)
        if (block.timestamp > getAutomatedReportDueTimestamp()):
            return(0)
        return(1)

    def isInAutomatedDisputePhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (block.timestamp < getAutomatedReportDueTimestamp()):
            return(0)
        if (block.timestamp > getAutomatedReportDisputeDueTimestamp()):
            return(0)
        return(1)

    def isInLimitedReportingPhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (not reportingWindow.isReportingActive()):
            return(0)
        if (limitedReportersDisputeBondToken):
            return(0)
        if (automatedReportReceived and not automatedReporterDisputeBondToken):
            return(0)
        return(1)

    def isInLimitedDisputePhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (not reportingWindow.isDisputeActive()):
            return(0)
        if (limitedReportersDisputeBondToken):
            return(0)
        if (automatedReportReceived and not automatedReporterDisputeBondToken):
            return(0)
        return(1)

    def isInAllReportingPhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (not reportingWindow.isReportingActive()):
            return(0)
        if (not limitedReportersDisputeBondToken):
            return(0)
        if (allReportersDisputeBondToken):
            return(0)
        if (automatedReportReceived and not automatedReporterDisputeBondToken):
            return(0)
        return(1)

    def isInAllDisputePhase():
        assertNoValue()
        if (isFinalized()):
            return(0)
        if (not reportingWindow.isDisputeActive()):
            return(0)
        if (not limitedReportersDisputeBondToken):
            return(0)
        if (allReportersDisputeBondToken):
            return(0)
        if (automatedReportReceived and not automatedReporterDisputeBondToken):
            return(0)
        return(1)

    def isContainerForReportingToken(shadyToken: address):
        assertNoValue()
        if (not shadyToken):
            return(0)
        if (shadyToken.getTypeName() != "ReportingToken"):
            return(0)
        shadyId = shadyToken.getPayoutDistributionHash()
        if (not reportingTokens.contains(shadyId)):
            return(0)
        if (reportingTokens.getValue(shadyId) != shadyToken):
            return(0)
        return(1)

    def isContainerForShareToken(shadyShareToken: address):
        if (shadyShareToken.getTypeName() != "ShareToken"):
            return(0)
        outcome = shadyShareToken.getOutcome()
        return(getShareToken(outcome) == shadyShareToken)

    def isContainerForDisputeBondToken(shadyBondToken: address):
        if (shadyBondToken.getTypeName() != "DisputeBondToken"):
            return(0)
        if (automatedReporterDisputeBondToken == shadyBondToken):
            return(1)
        elif (limitedReportersDisputeBondToken == shadyBondToken):
            return(1)
        elif (allReportersDisputeBondToken == shadyBondToken):
            return(1)
        return(0)

    def canBeReportedOn():
        assertNoValue()
        // CONSIDER: should we check if migration is necessary here?
        if (isFinalized()):
            return(0)
        if (not reportingWindow.isReportingActive()):
            return(0)
        return(1)

    def needsMigration():
        assertNoValue()
        if (isFinalized()):
            return(0)
        forkingMarket = getBranch().getForkingMarket()
        if (not forkingMarket):
            return(0)
        if (forkingMarket == this):
            return(0)
        if (block.timestamp < endTime):
            return(0)
        if (automatedReporterAddress and block.timestamp < getAutomatedReportDueTimestamp()):
            return(0)
        if (automatedReportReceived and block.timestamp < getAutomatedReportDisputeDueTimestamp()):
            return 0
        if (automatedReportReceived and not automatedReporterDisputeBondToken):
            return 0
        return(1)

    def getAutomatedReportDueTimestamp():
        assertNoValue()
        return(endTime + AUTOMATED_REPORTING_DURATION_SECONDS)

    def getAutomatedReportDisputeDueTimestamp():
        assertNoValue()
        return(getAutomatedReportDueTimestamp() + AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS)

}
// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/ReputationToken.sol';
import 'ROOT/reporting/DisputeBondToken.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/trading/Cash.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/extensions/MarketFeeCalculator.sol';
import 'ROOT/factories/MapFactory.sol';
import 'ROOT/factories/ShareTokenFactory.sol';
import 'ROOT/factories/ReportingTokenFactory.sol';
import 'ROOT/factories/DisputeBondTokenFactory.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/ERC20Basic.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/math/SafeMathInt256.sol';


contract Market is DelegationTarget, Typed, Initializable {
    using SafeMathUint256 for uint256;
    using SafeMathInt256 for int256;

    enum ReportingState {
        AUTOMATED,
        LIMITED,
        ALL,
        FORK,
        FINALIZED
    }

    ReportingState private reportingState = ReportingState.AUTOMATED;

    // CONSIDER: change the payoutNumerator/payoutDenominator to use fixed point numbers instead of integers; PRO: some people find fixed point decimal values easier to grok; CON: rounding errors can occur and it is easier to screw up the math if you don't handle fixed point values correctly
    uint256 public payoutDenominator;
    uint256 public feePerEthInAttoeth;

    // CONSIDER: we really don't need these
    int256 public maxDisplayPrice;
    int256 public minDisplayPrice;

    // CONSIDER: figure out approprate values for these
    uint256 private constant AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20;
    uint256 private constant LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21;
    uint256 private constant ALL_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22;

    uint256 private constant MIN_NUM_OUTCOMES = 2;
    uint256 private constant MIN_PAYOUT_DENOMINATOR = 2;
    uint256 private constant MAX_FEE_PER_ETH_IN_ATTOETH = 5 * 10 ** 17;
    int256 private constant DISPLAY_PRICE_MIN = -(2 ** 254);
    int256 private constant DISPLAY_PRICE_MAX = 2 ** 254;
    uint256 private constant SET_COST_MULTIPLIER_MAX = 2 ** 254;
    uint256 private constant APPROVAL_AMOUNT = 2 ** 254;
    uint256 private constant AUTOMATED_REPORTING_DURATION_SECONDS = 3 days;
    uint256 private constant AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
    address private constant NULL_ADDRESS = address(0);

    ReportingWindow public reportingWindow;
    uint256 public endTime;
    uint8 public numOutcomes;
    uint256 private marketCreationBlock;
    bytes32 public topic;
    address private automatedReporterAddress;
    mapping(bytes32 => ReportingToken) private reportingTokens;
    Cash public denominationToken;
    address public creator;
    IShareToken[] private shareTokens;
    uint256 public finalizationTime;
    bool private automatedReportReceived;
    bytes32 public tentativeWinningPayoutDistributionHash;
    bytes32 public finalPayoutDistributionHash;
    DisputeBondToken public automatedReporterDisputeBondToken;
    DisputeBondToken public limitedReportersDisputeBondToken;
    DisputeBondToken public allReportersDisputeBondToken;
    uint256 private validityBondAttoeth;
    uint256 private automatedReporterBondAttoeth;

    function initialize(ReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _payoutDenominator, uint256 _feePerEthInAttoeth, Cash _denominationToken, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) public payable beforeInitialized returns (bool _success) {
        endInitialization();
        require(address(_reportingWindow) != NULL_ADDRESS);
        require(_payoutDenominator >= MIN_PAYOUT_DENOMINATOR);
        require(_numOutcomes >= MIN_NUM_OUTCOMES);
        // payoutDenominator must be a multiple of numOutcomes so we can evenly split complete set share payout on indeterminate
        require((_payoutDenominator % _numOutcomes) == 0);
        require(feePerEthInAttoeth <= MAX_FEE_PER_ETH_IN_ATTOETH);
        require((DISPLAY_PRICE_MIN <= _maxDisplayPrice) && (_maxDisplayPrice <= DISPLAY_PRICE_MAX));
        require((DISPLAY_PRICE_MIN <= _minDisplayPrice) && (_minDisplayPrice <= DISPLAY_PRICE_MAX));
        require((1 <= uint256(_maxDisplayPrice.sub(_minDisplayPrice))) && (uint256(_maxDisplayPrice.sub(_minDisplayPrice)) <= SET_COST_MULTIPLIER_MAX));
        require(_creator != NULL_ADDRESS);
        // FIXME: require market to be on a non-forking branch; repeat this check up the stack as well if necessary (e.g., in reporting window)
        // CONSIDER: should we allow creator to send extra ETH, is there risk of variability in bond requirements?
        require(msg.value == MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getMarketCreationCost(_reportingWindow));
        reportingWindow = _reportingWindow;
        endTime = _endTime;
        numOutcomes = _numOutcomes;
        payoutDenominator = _payoutDenominator;
        // FIXME: markets may be denominated in tokens that aren't 10^18, deal with that
        feePerEthInAttoeth = _feePerEthInAttoeth;
        maxDisplayPrice = _maxDisplayPrice;
        minDisplayPrice = _minDisplayPrice;
        marketCreationBlock = block.number;
        topic = _topic;
        automatedReporterAddress = _automatedReporterAddress;
        denominationToken = _denominationToken;
        creator = _creator;
        for (uint8 _outcome = 0; _outcome < numOutcomes; _outcome++) {
            shareTokens.push(createShareToken(_outcome));
        }
        approveSpenders();
        require(controller.lookup("Cash") == address(denominationToken) || getBranch().isContainerForShareToken(denominationToken));
        _success = true;
        return _success;
    }

    function createShareToken(uint8 _outcome) private returns (IShareToken) {
        return ShareTokenFactory(controller.lookup("ShareTokenFactory")).createShareToken(controller, this, _outcome);
    }

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
    function approveSpenders() private returns (bool) {
        bytes32[5] memory _names = [bytes32("cancelOrder"), bytes32("completeSets"), bytes32("takeOrder"), bytes32("tradingEscapeHatch"), bytes32("claimProceeds")];
        uint8 i = 0;
        for (i = 0; i < 5; i++) {
            denominationToken.approve(controller.lookup(_names[i]), APPROVAL_AMOUNT);
        }
        for (i = 0; i < numOutcomes; i++) {
            shareTokens[i].approve(controller.lookup("takeOrder"), APPROVAL_AMOUNT);
        }
        return true;
    }

    function changeCreator(address _newCreator) public returns (bool) {
        require(msg.sender == creator);
        creator = _newCreator;
        return true;
    }

    function decreaseMarketCreatorSettlementFeeInAttoethPerEth(uint256 _newFeePerEthInWei) public returns (bool) {
        require(_newFeePerEthInWei < feePerEthInAttoeth);
        require(msg.sender == creator);
        feePerEthInAttoeth = _newFeePerEthInWei;
        return true;
    }

    function automatedReport(uint256[] _payoutNumerators) public returns (bool) {
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(msg.sender == automatedReporterAddress);
        require(isInAutomatedReportingPhase());
        // we have to create the reporting token so the rest of the system works (winning reporting token must exist)
        getReportingToken(_payoutNumerators);
        automatedReportReceived = true;
        tentativeWinningPayoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        reportingWindow.updateMarketPhase();
        return true;
    }

    function disputeAutomatedReport() public returns (bool) {
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(isInAutomatedDisputePhase());
        automatedReporterDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingState = ReportingState.LIMITED;
        fundDisputeBondWithReputation(msg.sender, automatedReporterDisputeBondToken, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT);
        reportingWindow.updateMarketPhase();
        return true;
    }

    function disputeLimitedReporters() public returns (bool) {
        migrateThroughAllForks();
        require(isInLimitedDisputePhase());
        limitedReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingState = ReportingState.ALL;
        fundDisputeBondWithReputation(msg.sender, limitedReportersDisputeBondToken, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT);
        ReportingWindow _newReportingWindow = getBranch().getNextReportingWindow();
        return migrateReportingWindow(_newReportingWindow);
    }

    function disputeAllReporters() public returns (bool) {
        migrateThroughAllForks();
        require(isInAllDisputePhase());
        allReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, ALL_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingState = ReportingState.FORK;
        fundDisputeBondWithReputation(msg.sender, allReportersDisputeBondToken, ALL_REPORTERS_DISPUTE_BOND_AMOUNT);
        reportingWindow.getBranch().fork();
        ReportingWindow _newReportingWindow = getBranch().getReportingWindowForForkEndTime();
        return migrateReportingWindow(_newReportingWindow);
    }

    function migrateReportingWindow(ReportingWindow _newReportingWindow) private returns (bool) {
        _newReportingWindow.migrateMarketInFromSibling();
        reportingWindow.removeMarket();
        reportingWindow = _newReportingWindow;
        return true;
    }

    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) {
        ReportingToken _reportingToken = reportingTokens[_payoutDistributionHash];
        require(address(_reportingToken) != NULL_ADDRESS);

        ReportingToken _tentativeWinningReportingToken = reportingTokens[tentativeWinningPayoutDistributionHash];
        if (address(_tentativeWinningReportingToken) == NULL_ADDRESS) {
            tentativeWinningPayoutDistributionHash = _payoutDistributionHash;
            _tentativeWinningReportingToken = _reportingToken;
        }
        if (_reportingToken.totalSupply() > _tentativeWinningReportingToken.totalSupply()) {
            tentativeWinningPayoutDistributionHash = _payoutDistributionHash;
        }
        return true;
    }

    function tryFinalize() public returns (bool) {
        require(tentativeWinningPayoutDistributionHash != bytes32(0));

        if (isFinalized()) {
            return true;
        }

        if (reportingState == ReportingState.AUTOMATED) {
            if (!automatedReportReceived) {
                if (reportingWindow.isReportingActive()) {
                    reportingState = ReportingState.LIMITED;
                } else {
                    return false;
                }
            }
            if (block.timestamp < getAutomatedReportDisputeDueTimestamp()) {
                return false;
            }
        }
        if (reportingState == ReportingState.LIMITED || reportingState == ReportingState.ALL) {
            migrateThroughAllForks();

            if (block.timestamp <= reportingWindow.getEndTime()) {
                return false;
            }
        }
        if (reportingState == ReportingState.FORK) {
            if (!tryFinalizeFork()) {
                return false;
            }
        }

        finalPayoutDistributionHash = tentativeWinningPayoutDistributionHash;
        finalizationTime = block.timestamp;
        transferIncorrectDisputeBondsToWinningReportingToken();
        reportingWindow.updateMarketPhase();
        reportingState = ReportingState.FINALIZED;
        return true;
    }

        // FIXME: when the market is finalized, we need to add `reportingTokens[finalPayoutDistributionHash].totalSupply()` to the reporting window.  This is necessary for fee collection which is a cross-market operation.
        // TODO: figure out how to make it so fee distribution is delayed until all markets have been finalized; we can enforce it contract side and let the UI deal with the actual work
        // FIXME: if finalPayoutDistributionHash != getIdentityDistributionId(), pay back validity bond holder
        // FIXME: if finalPayoutDistributionHash == getIdentityDistributionId(), transfer validity bond to reportingWindow (reporter fee pot)
        // FIXME: if automated report is wrong, transfer automated report bond to reportingWindow
        // FIXME: if automated report is right, transfer automated report bond to market creator
        // FIXME: handle markets that get 0 reports during their scheduled reporting window

    function tryFinalizeFork() private returns (bool) {
        bytes32 _winningPayoutDistributionHash = reportingWindow.getWinningPayoutDistributionHashFromFork(this);
        if (_winningPayoutDistributionHash == bytes32(0)) {
            return false;
        }
        tentativeWinningPayoutDistributionHash = _winningPayoutDistributionHash;
        return true;
    }

    function migrateThroughAllForks() public returns (bool) {
        // this will loop until we run out of gas, follow forks until there are no more, or have reached an active fork (which will throw)
        while (migrateThroughOneFork()) {
            continue;
        }
        return true;
    }

    // returns 0 if no move occurs, 1 if move occurred, throws if a fork not yet resolved
    function migrateThroughOneFork() public returns (bool) {
        if (isFinalized()) {
            return true;
        }
        if (!needsMigration()) {
            return false;
        }
        // only proceed if the forking market is finalized
        require(reportingWindow.isForkingMarketFinalized());
        Branch _currentBranch = getBranch();
        // follow the forking market to its branch and then attach to the next reporting window on that branch
        bytes32 _winningForkPayoutDistributionHash = _currentBranch.getForkingMarket().finalPayoutDistributionHash();
        Branch _destinationBranch = _currentBranch.getChildBranch(_winningForkPayoutDistributionHash);
        ReportingWindow _newReportingWindow = _destinationBranch.getNextReportingWindow();
        _newReportingWindow.migrateMarketInFromNibling();
        reportingWindow.removeMarket();
        reportingWindow = _newReportingWindow;
        // reset to unreported state
        limitedReportersDisputeBondToken = DisputeBondToken(0);
        allReportersDisputeBondToken = DisputeBondToken(0);
        tentativeWinningPayoutDistributionHash = 0;
        return true;
    }

    ////////
    //////// Helpers
    ////////

    function getReportingToken(uint256[] _payoutNumerators) public returns (ReportingToken) {
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        ReportingToken _reportingToken = reportingTokens[_payoutDistributionHash];
        if (address(_reportingToken) == NULL_ADDRESS) {
            _reportingToken = ReportingTokenFactory(controller.lookup("ReportingTokenFactory")).createReportingToken(controller, this, _payoutNumerators);
            reportingTokens[_payoutDistributionHash] = _reportingToken;
        }
        return _reportingToken;
    }

    function fundDisputeBondWithReputation(address _bondHolder, DisputeBondToken _disputeBondToken, uint256 _bondAmount) private returns (bool) {
        require(_bondHolder == _disputeBondToken.getBondHolder());
        reportingWindow.getReputationToken().trustedTransfer(_bondHolder, _disputeBondToken, _bondAmount);
        return true;
    }

    function transferIncorrectDisputeBondsToWinningReportingToken() private returns (bool) {
        require(isFinalized());
        ReputationToken _reputationToken = reportingWindow.getReputationToken();
        if (getBranch().getForkingMarket() == this) {
            return true;
        }
        if (address(automatedReporterDisputeBondToken) != NULL_ADDRESS && automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() == finalPayoutDistributionHash) {
            _reputationToken.trustedTransfer(automatedReporterDisputeBondToken, getFinalWinningReportingToken(), _reputationToken.balanceOf(automatedReporterDisputeBondToken));
        }
        if (address(limitedReportersDisputeBondToken) != NULL_ADDRESS && limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() == finalPayoutDistributionHash) {
            _reputationToken.trustedTransfer(limitedReportersDisputeBondToken, getFinalWinningReportingToken(), _reputationToken.balanceOf(limitedReportersDisputeBondToken));
        }
        return true;
    }

    function derivePayoutDistributionHash(uint256[] _payoutNumerators) public constant returns (bytes32) {
        uint256 _sum = 0;
        require(_payoutNumerators.length == numOutcomes);
        for (uint8 i = 0; i < numOutcomes; i++) {
            require(_payoutNumerators[i] <= payoutDenominator);
            _sum += _payoutNumerators[i];
        }
        require(_sum == payoutDenominator);
        return sha3(_payoutNumerators);
    }

    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public constant returns (ReportingToken) {
        return reportingTokens[_payoutDistributionHash];
    }

    ////////
    //////// Getters
    ////////
    function getTypeName() public constant returns (bytes32) {
        return "Market";
    }

    function getBranch() public constant returns (Branch) {
        return reportingWindow.getBranch();
    }

    function getFinalWinningReportingToken() public constant returns (ReportingToken) {
        return reportingTokens[finalPayoutDistributionHash];
    }

    function getShareToken(uint8 outcome)  public constant returns (IShareToken) {
        require(outcome < numOutcomes);
        return shareTokens[outcome];
    }

    function getCompleteSetCostInAttotokens() public constant returns (uint256) {
        return uint256(maxDisplayPrice.sub(minDisplayPrice));
    }

    function shouldCollectReportingFees() public constant returns (bool) {
        return !getBranch().isContainerForShareToken(denominationToken);
    }

    function isDoneWithAutomatedReporters() public constant returns (bool) {
        return automatedReportReceived || block.timestamp > getAutomatedReportDueTimestamp();
    }

    function isDoneWithLimitedReporters() public constant returns (bool) {
        return isDoneWithReporters(ReportingState.LIMITED);
    }

    function isDoneWithAllReporters() public constant returns (bool) {
        return isDoneWithReporters(ReportingState.ALL);
    }

    function isDoneWithReporters(ReportingState _state) private constant returns (bool) {
        if (reportingState > _state) {
            return true;
        }
        if (block.timestamp > reportingWindow.getEndTime()) {
            return true;
        }
        return false;
    }

    function isFinalized() public constant returns (bool) {
        return finalPayoutDistributionHash != bytes32(0);
    }

    function isInAutomatedReportingPhase() public constant returns (bool) {
        if (isFinalized()) {
            return false;
        }
        if (block.timestamp < endTime) {
            return false;
        }
        if (block.timestamp > getAutomatedReportDueTimestamp()) {
            return false;
        }
        return true;
    }

    function isInAutomatedDisputePhase() public constant returns (bool) {
        if (isFinalized()) {
            return false;
        }
        if (block.timestamp < getAutomatedReportDueTimestamp()) {
            return false;
        }
        if (block.timestamp > getAutomatedReportDisputeDueTimestamp()) {
            return false;
        }
        return true;
    }

    function isInLimitedReportingPhase() public constant returns (bool) {
        if (!canBeReportedOn()) {
            return false;
        }
        if (reportingState > ReportingState.LIMITED) {
            return false;
        }
        return true;
    }

    function isInLimitedDisputePhase() public constant returns (bool) {
        if (!reportingWindow.isDisputeActive()) {
            return false;
        }
        if (reportingState > ReportingState.LIMITED) {
            return false;
        }
        return true;
    }

    function isInAllReportingPhase() public constant returns (bool) {
        if (!canBeReportedOn()) {
            return false;
        }
        if (reportingState != ReportingState.ALL) {
            return false;
        }
        return true;
    }

    function isInAllDisputePhase() public constant returns (bool) {
        if (!reportingWindow.isDisputeActive()) {
            return false;
        }
        if (reportingState != ReportingState.ALL) {
            return false;
        }
        return true;
    }

    function isContainerForReportingToken(ReportingToken _shadyToken) public constant returns (bool) {
        if (address(_shadyToken) == NULL_ADDRESS) {
            return false;
        }
        if (_shadyToken.getTypeName() != "ReportingToken") {
            return false;
        }
        bytes32 _shadyId = _shadyToken.getPayoutDistributionHash();
        ReportingToken _reportingToken = reportingTokens[_shadyId];
        if (address(_reportingToken) == NULL_ADDRESS) {
            return false;
        }
        if (_reportingToken != _shadyToken) {
            return false;
        }
        return true;
    }

    function isContainerForShareToken(IShareToken _shadyShareToken) public constant returns (bool) {
        if (_shadyShareToken.getTypeName() != "ShareToken") {
            return false;
        }
        return(getShareToken(_shadyShareToken.getOutcome()) == _shadyShareToken);
    }

    function isContainerForDisputeBondToken(DisputeBondToken _shadyBondToken) public constant returns (bool) {
        if (_shadyBondToken.getTypeName() != "DisputeBondToken") {
            return false;
        }
        if (automatedReporterDisputeBondToken == _shadyBondToken) {
            return true;
        } else if (limitedReportersDisputeBondToken == _shadyBondToken) {
            return true;
        } else if (allReportersDisputeBondToken == _shadyBondToken) {
            return true;
        }
        return false;
    }

    function canBeReportedOn() public constant returns (bool) {
        // CONSIDER: should we check if migration is necessary here?
        if (isFinalized()) {
            return false;
        }
        if (!reportingWindow.isReportingActive()) {
            return false;
        }
        return true;
    }

    function needsMigration() public constant returns (bool) {
        if (isFinalized()) {
            return false;
        }
        Market _forkingMarket = getBranch().getForkingMarket();
        if (address(_forkingMarket) == NULL_ADDRESS) {
            return false;
        }
        if (_forkingMarket == this) {
            return false;
        }
        if (block.timestamp < endTime) {
            return false;
        }
        if (automatedReporterAddress != NULL_ADDRESS && block.timestamp < getAutomatedReportDueTimestamp()) {
            return false;
        }
        if (automatedReportReceived && block.timestamp < getAutomatedReportDisputeDueTimestamp()) {
            return false;
        }
        if (automatedReportReceived && address(automatedReporterDisputeBondToken) == NULL_ADDRESS) {
            return false;
        }
        return true;
    }

    function getAutomatedReportDueTimestamp() public constant returns (uint256) {
        return endTime + AUTOMATED_REPORTING_DURATION_SECONDS;
    }

    function getAutomatedReportDisputeDueTimestamp() public constant returns (uint256) {
        return getAutomatedReportDueTimestamp() + AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS;
    }
}
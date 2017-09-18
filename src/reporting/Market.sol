pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/Ownable.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IDisputeBond.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/trading/IShareToken.sol';
import 'ROOT/extensions/MarketExtensions.sol';
import 'ROOT/extensions/MarketFeeCalculator.sol';
import 'ROOT/factories/ShareTokenFactory.sol';
import 'ROOT/factories/ReportingTokenFactory.sol';
import 'ROOT/factories/DisputeBondTokenFactory.sol';
import 'ROOT/libraries/token/ERC20Basic.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/math/SafeMathInt256.sol';
import 'ROOT/reporting/Reporting.sol';


contract Market is DelegationTarget, Typed, Initializable, Ownable, IMarket {
    using SafeMathUint256 for uint256;
    using SafeMathInt256 for int256;

    // CONSIDER: change the payoutNumerator/payoutDenominator to use fixed point numbers instead of integers; PRO: some people find fixed point decimal values easier to grok; CON: rounding errors can occur and it is easier to screw up the math if you don't handle fixed point values correctly
    uint256 private payoutDenominator;
    uint256 private feePerEthInAttoeth;

    // CONSIDER: we really don't need these
    int256 private maxDisplayPrice;
    int256 private minDisplayPrice;

    // CONSIDER: figure out approprate values for these
    uint256 private constant AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20;
    uint256 private constant LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21;
    uint256 private constant ALL_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22;

    uint256 private constant MAX_FEE_PER_ETH_IN_ATTOETH = 5 * 10 ** 17;
    uint256 private constant APPROVAL_AMOUNT = 2 ** 254;
    address private constant NULL_ADDRESS = address(0);

    IReportingWindow private reportingWindow;
    uint256 private endTime;
    uint8 private numOutcomes;
    uint256 private marketCreationBlock;
    bytes32 private topic;
    address private automatedReporterAddress;
    mapping(bytes32 => IReportingToken) private reportingTokens;
    ICash private cash;
    IShareToken[] private shareTokens;
    uint256 private finalizationTime;
    uint256 private automatedReportReceivedTime;
    bytes32 private tentativeWinningPayoutDistributionHash;
    bytes32 private finalPayoutDistributionHash;
    IDisputeBond private automatedReporterDisputeBondToken;
    IDisputeBond private limitedReportersDisputeBondToken;
    IDisputeBond private allReportersDisputeBondToken;
    uint256 private validityBondAttoeth;
    uint256 private automatedReporterBondAttoeth;

    /**
     * @dev Makes the function trigger a migration before execution
     */
    modifier triggersMigration() {
        migrateThroughAllForks();
        _;
    }

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _payoutDenominator, uint256 _feePerEthInAttoeth, ICash _cash, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) public payable beforeInitialized returns (bool _success) {
        endInitialization();
        require(address(_reportingWindow) != NULL_ADDRESS);
        require(_numOutcomes >= 2);
        require(_numOutcomes <= 8);
        // payoutDenominator must be a multiple of numOutcomes so we can evenly split complete set share payout on indeterminate
        require((_payoutDenominator % _numOutcomes) == 0);
        require(feePerEthInAttoeth <= MAX_FEE_PER_ETH_IN_ATTOETH);
        require(_minDisplayPrice < _maxDisplayPrice);
        require(_creator != NULL_ADDRESS);
        require(_cash.getTypeName() == "Cash");
        // FIXME: require market to be on a non-forking branch; repeat this check up the stack as well if necessary (e.g., in reporting window)
        // CONSIDER: should we allow creator to send extra ETH, is there risk of variability in bond requirements?
        require(msg.value == MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getMarketCreationCost(_reportingWindow));
        reportingWindow = _reportingWindow;
        endTime = _endTime;
        numOutcomes = _numOutcomes;
        payoutDenominator = _payoutDenominator;
        feePerEthInAttoeth = _feePerEthInAttoeth;
        maxDisplayPrice = _maxDisplayPrice;
        minDisplayPrice = _minDisplayPrice;
        marketCreationBlock = block.number;
        topic = _topic;
        automatedReporterAddress = _automatedReporterAddress;
        cash = _cash;
        owner = _creator;
        for (uint8 _outcome = 0; _outcome < numOutcomes; _outcome++) {
            shareTokens.push(createShareToken(_outcome));
        }
        approveSpenders();
        return true;

        // TODO: we need to update this signature (and all of the places that call it) to allow the creator (UI) to pass in a number of other things which will all be logged here
        // TODO: log short description
        // TODO: log long description
        // TODO: log min display price
        // TODO: log max display price
        // TODO: log tags (0-2)
        // TODO: log outcome labels (same number as numOutcomes)
        // TODO: log type (scalar, binary, categorical)
        // TODO: log any immutable data associated with the market (e.g., endTime, numOutcomes, payoutDenominator, cash address, etc.)
    }

    function createShareToken(uint8 _outcome) private returns (IShareToken) {
        return ShareTokenFactory(controller.lookup("ShareTokenFactory")).createShareToken(controller, this, _outcome);
    }

    // this will need to be called manually for each open market if a spender contract is updated
    function approveSpenders() private returns (bool) {
        bytes32[5] memory _names = [bytes32("CancelOrder"), bytes32("CompleteSets"), bytes32("TakeOrder"), bytes32("TradingEscapeHatch"), bytes32("ClaimProceeds")];
        for (uint8 i = 0; i < _names.length; i++) {
            cash.approve(controller.lookup(_names[i]), APPROVAL_AMOUNT);
        }
        for (uint8 j = 0; j < numOutcomes; j++) {
            shareTokens[j].approve(controller.lookup("TakeOrder"), APPROVAL_AMOUNT);
        }
        return true;
    }

    function decreaseMarketCreatorSettlementFeeInAttoethPerEth(uint256 _newFeePerEthInWei) public onlyOwner returns (bool) {
        require(_newFeePerEthInWei < feePerEthInAttoeth);
        feePerEthInAttoeth = _newFeePerEthInWei;
        return true;
    }

    function automatedReport(uint256[] _payoutNumerators) public returns (bool) {
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(msg.sender == automatedReporterAddress);
        require(getReportingState() == ReportingState.AUTOMATED_REPORTING);
        // we have to create the reporting token so the rest of the system works (winning reporting token must exist)
        getReportingToken(_payoutNumerators);
        automatedReportReceivedTime = block.timestamp;
        tentativeWinningPayoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        reportingWindow.updateMarketPhase();
        return true;
    }

    function disputeAutomatedReport() public returns (bool) {
        // intentionally does not migrate the market as automated report markets won't actually migrate unless a dispute bond has been placed or the automated report doesn't occur
        require(getReportingState() == ReportingState.AUTOMATED_DISPUTE);
        automatedReporterDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingWindow.getReputationToken().trustedTransfer(msg.sender, automatedReporterDisputeBondToken, AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT);
        reportingWindow.updateMarketPhase();
        return true;
    }

    function disputeLimitedReporters() public triggersMigration returns (bool) {
        require(getReportingState() == ReportingState.LIMITED_DISPUTE);
        limitedReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingWindow.getReputationToken().trustedTransfer(msg.sender, limitedReportersDisputeBondToken, LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT);
        IReportingWindow _newReportingWindow = getBranch().getNextReportingWindow();
        return migrateReportingWindow(_newReportingWindow);
    }

    function disputeAllReporters() public triggersMigration returns (bool) {
        require(getReportingState() == ReportingState.ALL_DISPUTE);
        allReportersDisputeBondToken = DisputeBondTokenFactory(controller.lookup("DisputeBondTokenFactory")).createDisputeBondToken(controller, this, msg.sender, ALL_REPORTERS_DISPUTE_BOND_AMOUNT, tentativeWinningPayoutDistributionHash);
        reportingWindow.getReputationToken().trustedTransfer(msg.sender, allReportersDisputeBondToken, ALL_REPORTERS_DISPUTE_BOND_AMOUNT);
        reportingWindow.getBranch().fork();
        IReportingWindow _newReportingWindow = getBranch().getReportingWindowForForkEndTime();
        return migrateReportingWindow(_newReportingWindow);
    }

    function migrateReportingWindow(IReportingWindow _newReportingWindow) private afterInitialized returns (bool) {
        _newReportingWindow.migrateMarketInFromSibling();
        reportingWindow.removeMarket();
        reportingWindow = _newReportingWindow;
        reportingWindow.updateMarketPhase();
        return true;
    }

    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) {
        IReportingToken _reportingToken = reportingTokens[_payoutDistributionHash];
        require(address(_reportingToken) != NULL_ADDRESS);

        IReportingToken _tentativeWinningReportingToken = reportingTokens[tentativeWinningPayoutDistributionHash];
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

        if (getReportingState() != ReportingState.AWAITING_FINALIZATION) {
            return false;
        }

        if (getBranch().getForkingMarket() == this) {
            tentativeWinningPayoutDistributionHash = getWinningPayoutDistributionHashFromFork();
        }
        finalPayoutDistributionHash = tentativeWinningPayoutDistributionHash;
        finalizationTime = block.timestamp;
        transferIncorrectDisputeBondsToWinningReportingToken();
        reportingWindow.updateMarketPhase();
        return true;

        // FIXME: when the market is finalized, we need to add `reportingTokens[finalPayoutDistributionHash].totalSupply()` to the reporting window.  This is necessary for fee collection which is a cross-market operation.
        // TODO: figure out how to make it so fee distribution is delayed until all markets have been finalized; we can enforce it contract side and let the UI deal with the actual work
        // FIXME: if finalPayoutDistributionHash != getIdentityDistributionId(), pay back validity bond holder
        // FIXME: if finalPayoutDistributionHash == getIdentityDistributionId(), transfer validity bond to reportingWindow (reporter fee pot)
        // FIXME: if automated report is wrong, transfer automated report bond to reportingWindow
        // FIXME: if automated report is right, transfer automated report bond to market creator
        // FIXME: handle markets that get 0 reports during their scheduled reporting window. We should move to the next reporting window in this case.
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
        if (getReportingState() != ReportingState.AWAITING_MIGRATION) {
            return false;
        }
        // only proceed if the forking market is finalized
        require(reportingWindow.isForkingMarketFinalized());
        IBranch _currentBranch = getBranch();
        // follow the forking market to its branch and then attach to the next reporting window on that branch
        bytes32 _winningForkPayoutDistributionHash = _currentBranch.getForkingMarket().getFinalPayoutDistributionHash();
        IBranch _destinationBranch = _currentBranch.getOrCreateChildBranch(_winningForkPayoutDistributionHash);
        IReportingWindow _newReportingWindow = _destinationBranch.getNextReportingWindow();
        _newReportingWindow.migrateMarketInFromNibling();
        reportingWindow.removeMarket();
        reportingWindow = _newReportingWindow;
        reportingWindow.updateMarketPhase();
        // reset to unreported state
        limitedReportersDisputeBondToken = IDisputeBond(0);
        allReportersDisputeBondToken = IDisputeBond(0);
        tentativeWinningPayoutDistributionHash = bytes32(0);
        return true;
    }

    //
    // Helpers
    //

    function getReportingToken(uint256[] _payoutNumerators) public returns (IReportingToken) {
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        IReportingToken _reportingToken = reportingTokens[_payoutDistributionHash];
        if (address(_reportingToken) == NULL_ADDRESS) {
            _reportingToken = ReportingTokenFactory(controller.lookup("ReportingTokenFactory")).createReportingToken(controller, this, _payoutNumerators);
            reportingTokens[_payoutDistributionHash] = _reportingToken;
        }
        return _reportingToken;
    }

    function transferIncorrectDisputeBondsToWinningReportingToken() private returns (bool) {
        require(getReportingState() == ReportingState.FINALIZED);
        IReputationToken _reputationToken = reportingWindow.getReputationToken();
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
        for (uint8 i = 0; i < _payoutNumerators.length; i++) {
            require(_payoutNumerators[i] <= payoutDenominator);
            _sum = _sum.add(_payoutNumerators[i]);
        }
        require(_sum == payoutDenominator);
        return sha3(_payoutNumerators);
    }

    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public constant returns (IReportingToken) {
        return reportingTokens[_payoutDistributionHash];
    }

    //
    //Getters
    //

    function getTypeName() public constant returns (bytes32) {
        return "Market";
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return reportingWindow;
    }

    function getBranch() public constant returns (IBranch) {
        return reportingWindow.getBranch();
    }

    function getAutomatedReporterDisputeBondToken() public constant returns (IDisputeBond) {
        return automatedReporterDisputeBondToken;
    }

    function getLimitedReportersDisputeBondToken() public constant returns (IDisputeBond) {
        return limitedReportersDisputeBondToken;
    }

    function getAllReportersDisputeBondToken() public constant returns (IDisputeBond) {
        return allReportersDisputeBondToken;
    }

    function getNumberOfOutcomes() public constant returns (uint8) {
        return numOutcomes;
    }

    function getEndTime() public constant returns (uint256) {
        return endTime;
    }

    function getTentativeWinningPayoutDistributionHash() public constant returns (bytes32) {
        return tentativeWinningPayoutDistributionHash;
    }

    function getFinalWinningReportingToken() public constant returns (IReportingToken) {
        return reportingTokens[finalPayoutDistributionHash];
    }

    function getShareToken(uint8 _outcome)  public constant returns (IShareToken) {
        require(_outcome < numOutcomes);
        return shareTokens[_outcome];
    }

    function getFinalPayoutDistributionHash() public constant returns (bytes32) {
        return finalPayoutDistributionHash;
    }

    function getPayoutDenominator() public constant returns (uint256) {
        return payoutDenominator;
    }

    function getDenominationToken() public constant returns (ICash) {
        return cash;
    }

    function getMarketCreatorSettlementFeeInAttoethPerEth() public constant returns (uint256) {
        return feePerEthInAttoeth;
    }

    function getMaxDisplayPrice() public constant returns (int256) {
        return maxDisplayPrice;
    }

    function getMinDisplayPrice() public constant returns (int256) {
        return minDisplayPrice;
    }

    function getCompleteSetCostInAttotokens() public constant returns (uint256) {
        return uint256(maxDisplayPrice.sub(minDisplayPrice));
    }

    function getTopic() public constant returns (bytes32) {
        return topic;
    }

    function getFinalizationTime() public constant returns (uint256) {
        return finalizationTime;
    }

    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool) {
        if (_shadyTarget.getTypeName() != "ReportingToken") {
            return false;
        }
        IReportingToken _shadyReportingToken = IReportingToken(_shadyTarget);
        bytes32 _shadyId = _shadyReportingToken.getPayoutDistributionHash();
        IReportingToken _reportingToken = reportingTokens[_shadyId];
        return _reportingToken == _shadyReportingToken;
    }

    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool) {
        if (_shadyTarget.getTypeName() != "ShareToken") {
            return false;
        }
        IShareToken _shadyShareToken = IShareToken(_shadyTarget);
        return getShareToken(_shadyShareToken.getOutcome()) == _shadyShareToken;
    }

    function isContainerForDisputeBondToken(Typed _shadyTarget) public constant returns (bool) {
        if (_shadyTarget.getTypeName() != "DisputeBondToken") {
            return false;
        }
        IDisputeBond _shadyDisputeBond = IDisputeBond(_shadyTarget);
        if (automatedReporterDisputeBondToken == _shadyDisputeBond) {
            return true;
        }
        if (limitedReportersDisputeBondToken == _shadyDisputeBond) {
            return true;
        }
        if (allReportersDisputeBondToken == _shadyDisputeBond) {
            return true;
        }
        return false;
    }

    function getAutomatedReportDueTimestamp() public constant returns (uint256) {
        if (automatedReportReceivedTime != 0) {
            return automatedReportReceivedTime;
        }
        return endTime + Reporting.automatedReportingDurationSeconds();
    }

    function getAutomatedReportDisputeDueTimestamp() public constant returns (uint256) {
        return getAutomatedReportDueTimestamp() + Reporting.automatedReportingDisputeDurationSeconds();
    }

    function getReportingState() public constant returns (ReportingState) {
        // Before trading in the market is finished
        if (block.timestamp < endTime) {
            return ReportingState.PRE_REPORTING;
        }

        // This market has been finalized
        if (finalPayoutDistributionHash != bytes32(0)) {
            return ReportingState.FINALIZED;
        }

        // Automated reporting period has not passed yet
        if (block.timestamp < getAutomatedReportDueTimestamp()) {
            return ReportingState.AUTOMATED_REPORTING;
        }

        bool _automatedReportDisputed = address(automatedReporterDisputeBondToken) != NULL_ADDRESS;
        bool _limitedReportDisputed = address(limitedReportersDisputeBondToken) != NULL_ADDRESS;

        // If we have an automated report that hasn't been disputed it is either in the dispute window or we can finalize the market
        if (automatedReportReceivedTime != 0 && !_automatedReportDisputed) {
            bool _beforeAutomatedDisputeDue = block.timestamp < getAutomatedReportDisputeDueTimestamp();
            return _beforeAutomatedDisputeDue ? ReportingState.AUTOMATED_DISPUTE : ReportingState.AWAITING_FINALIZATION;
        }

        // Since we've established that we're past automated reporting if there is an active fork we need to migrate
        IMarket _forkingMarket = getBranch().getForkingMarket();
        if (address(_forkingMarket) != NULL_ADDRESS && _forkingMarket != this) {
            return ReportingState.AWAITING_MIGRATION;
        }

        // If this market is the one forking we are in the process of migration or we're ready to finalize migration
        if (_forkingMarket == this) {
            if (getWinningPayoutDistributionHashFromFork() != bytes32(0)) {
                return ReportingState.AWAITING_FINALIZATION;
            }
            return ReportingState.FORKING;
        }

        // If a limited dispute bond has been posted we are in some phase of all reporting depending on time
        if (_limitedReportDisputed) {
            if (block.timestamp > reportingWindow.getEndTime()) {
                return ReportingState.AWAITING_FINALIZATION;
            }
            if (reportingWindow.isDisputeActive()) {
                return ReportingState.ALL_DISPUTE;
            }
            return ReportingState.ALL_REPORTING;
        }

        // Either no automated report was made or the automated report was disputed so we are in some phase of limited reporting
        if (block.timestamp > reportingWindow.getEndTime()) {
            return ReportingState.AWAITING_FINALIZATION;
        }

        if (reportingWindow.isDisputeActive()) {
            return ReportingState.LIMITED_DISPUTE;
        }

        return ReportingState.LIMITED_REPORTING;
    }

    function getWinningPayoutDistributionHashFromFork() private returns (bytes32) {
        return MarketExtensions(controller.lookup("MarketExtensions")).getWinningPayoutDistributionHashFromFork(this);
    }
}

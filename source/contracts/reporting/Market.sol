pragma solidity 0.4.18;

import 'reporting/IMarket.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/Ownable.sol';
import 'libraries/collections/Map.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingParticipant.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IReputationToken.sol';
import 'factories/DisputeCrowdsourcerFactory.sol';
import 'trading/ICash.sol';
import 'trading/IShareToken.sol';
import 'factories/ShareTokenFactory.sol';
import 'factories/InitialReporterFactory.sol';
import 'factories/MapFactory.sol';
import 'libraries/token/ERC20Basic.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/SafeMathInt256.sol';
import 'libraries/Extractable.sol';
import 'factories/MailboxFactory.sol';
import 'libraries/IMailbox.sol';
import 'reporting/Reporting.sol';
import 'reporting/IInitialReporter.sol';
import 'Augur.sol';


contract Market is DelegationTarget, Extractable, ITyped, Initializable, Ownable, IMarket {
    using SafeMathUint256 for uint256;
    using SafeMathInt256 for int256;

    // Constants
    uint256 private constant MAX_FEE_PER_ETH_IN_ATTOETH = 1 ether / 2;
    uint256 private constant APPROVAL_AMOUNT = 2**256-1;
    address private constant NULL_ADDRESS = address(0);
    uint8 private constant MIN_OUTCOMES = 2;
    uint8 private constant MAX_OUTCOMES = 8;

    // Contract Refs
    IUniverse private universe;
    IFeeWindow private feeWindow;
    ICash private cash;

    // Attributes
    uint256 private numTicks;
    uint256 private feeDivisor;
    uint256 private endTime;
    uint8 private numOutcomes;
    bytes32 private winningPayoutDistributionHash;
    uint256 private validityBondAttoeth;
    uint256 private reporterGasCostsFeeAttoeth;
    IMailbox private marketCreatorMailbox;
    bool private feeWindowMigrationRequired;
    uint256 private finalizationTime;

    // Collections
    IReportingParticipant[] public participants;
    Map public crowdsourcers;
    IShareToken[] private shareTokens;

    function initialize(IUniverse _universe, uint256 _endTime, uint256 _feePerEthInAttoeth, ICash _cash, address _designatedReporterAddress, address _creator, uint8 _numOutcomes, uint256 _numTicks) public onlyInGoodTimes payable beforeInitialized returns (bool _success) {
        endInitialization();
        require(MIN_OUTCOMES <= _numOutcomes && _numOutcomes <= MAX_OUTCOMES);
        require((_numTicks.isMultipleOf(_numOutcomes)));
        require(_feePerEthInAttoeth <= MAX_FEE_PER_ETH_IN_ATTOETH);
        require(_creator != NULL_ADDRESS);
        require(controller.getTimestamp() < _endTime);
        universe = _universe;
        require(getForkingMarket() == IMarket(0));
        owner = _creator;
        assessFees();
        endTime = _endTime;
        numOutcomes = _numOutcomes;
        numTicks = _numTicks;
        feeDivisor = 1 ether / _feePerEthInAttoeth;
        cash = _cash;
        InitialReporterFactory _initialReporterFactory = InitialReporterFactory(controller.lookup("InitialReporterFactory"));
        participants.push(_initialReporterFactory.createInitialReporter(controller, this, _designatedReporterAddress));
        marketCreatorMailbox = MailboxFactory(controller.lookup("MailboxFactory")).createMailbox(controller, owner);
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this);
        for (uint8 _outcome = 0; _outcome < numOutcomes; _outcome++) {
            shareTokens.push(createShareToken(_outcome));
        }
        approveSpenders();
        // If the value was not at least equal to the sum of these fees this will throw. The addition here cannot overflow as these fees are capped
        uint256 _refund = msg.value.sub(reporterGasCostsFeeAttoeth + validityBondAttoeth);
        if (_refund > 0) {
            require(owner.call.value(_refund)());
        }
        // Send the reporter gas bond to the initial report contract. It will be paid out only if they are correct.
        require(participants[0].call.value(reporterGasCostsFeeAttoeth)());
        return true;
    }

    function assessFees() private onlyInGoodTimes returns (bool) {
        IUniverse _universe = getUniverse();
        require(feeWindow.getReputationToken().balanceOf(this) == _universe.getOrCacheDesignatedReportNoShowBond());
        reporterGasCostsFeeAttoeth = _universe.getOrCacheTargetReporterGasCosts();
        validityBondAttoeth = _universe.getOrCacheValidityBond();
        return true;
    }

    function createShareToken(uint8 _outcome) private onlyInGoodTimes returns (IShareToken) {
        return ShareTokenFactory(controller.lookup("ShareTokenFactory")).createShareToken(controller, this, _outcome);
    }

    // This will need to be called manually for each open market if a spender contract is updated
    function approveSpenders() public onlyInGoodTimes returns (bool) {
        bytes32[5] memory _names = [bytes32("CancelOrder"), bytes32("CompleteSets"), bytes32("FillOrder"), bytes32("TradingEscapeHatch"), bytes32("ClaimTradingProceeds")];
        for (uint8 i = 0; i < _names.length; i++) {
            cash.approve(controller.lookup(_names[i]), APPROVAL_AMOUNT);
        }
        for (uint8 j = 0; j < numOutcomes; j++) {
            shareTokens[j].approve(controller.lookup("FillOrder"), APPROVAL_AMOUNT);
        }
        return true;
    }

    function doInitialReport(uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes returns (bool) {
        IInitialReporter _initialReporter = getInitialReporter();
        require(_initialReporter.getReportTimestamp() == 0);
        require(controller.getTimestamp() > endTime + Reporting.getDesignatedReportingDurationSeconds() || msg.sender == _initialReporter.getDesignatedReporter());
        distributeNoShowBond(_initialReporter);
        // The designated reporter must actually pay the required REP stake to report
        if (msg.sender == _initialReporter.getDesignatedReporter()) {
            IReputationToken _reputationToken = getReputationToken();
            _reputationToken.trustedMarketTransfer(msg.sender, _initialReporter, universe.getOrCacheDesignatedReportStake());
        }
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators, _invalid);
        feeWindow = universe.getOrCreateNextFeeWindow();
        _initialReporter.report(msg.sender, _payoutDistributionHash, _payoutNumerators, _invalid);
        return true;
    }

    function contribute(uint256[] _payoutNumerators, bool _invalid, uint256 _amount) public onlyInGoodTimes returns (bool) {
        require(feeWindow.isActive());
        // All participants trade in their existing fee window tokens for tokens in the new feeWindow
        if (feeWindowMigrationRequired) {
            for (uint8 i = 0; i < participants.length; i++) {
                participants[i].migrate();
            }
            feeWindowMigrationRequired = false;
        }
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators, _invalid);
        IDisputeCrowdsourcer _crowdsourcer = getOrCreateDisputeCrowdsourcer(_payoutDistributionHash, _payoutNumerators, _invalid);
        _crowdsourcer.contribute(msg.sender, _amount);
        return true;
    }

    function finishedCrowdsourcingDisputeBond() public onlyInGoodTimes returns (bool) {
        IReportingParticipant _reportingParticipant = IReportingParticipant(msg.sender);
        require(isContainerForReportingParticipant(_reportingParticipant));
        participants.push(_reportingParticipant);
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this); // disavow other crowdsourcers
        if (IDisputeCrowdsourcer(msg.sender).getSize() >= Reporting.getDisputeThresholdForFork()) {
            fork();
        } else {
            feeWindow = universe.getOrCreateNextFeeWindow();
            feeWindowMigrationRequired = true;
        }
        return true;
    }

    function finalize() public onlyInGoodTimes returns (bool) {
        if (universe.getForkingMarket() == this) {
            return finalizeFork();
        }

        require(winningPayoutDistributionHash == bytes32(0));
        require(getInitialReporter().getReportTimestamp() != 0);
        require(feeWindow.isOver());
        require(universe.getForkingMarket() == IMarket(0));
        feeWindow.onMarketFinalized();
        winningPayoutDistributionHash = participants[participants.length-1].getPayoutDistributionHash();
        redistributeLosingReputation();
        distributeValidityBond();
        finalizationTime = controller.getTimestamp();
        return true;
    }

    function finalizeFork() public onlyInGoodTimes returns (bool) {
        require(universe.getForkingMarket() == this);
        require(winningPayoutDistributionHash == bytes32(0));
        IUniverse _winningUniverse = universe.getWinningChildUniverse();
        winningPayoutDistributionHash = _winningUniverse.getParentPayoutDistributionHash();
        return true;
    }

    function redistributeLosingReputation() private returns (bool) {
        IReportingParticipant _reportingParticipant;

        // Initial pass is to liquidate losers so we have sufficient REP to pay the winners
        for (uint8 i = 0; i < participants.length; i++) {
            _reportingParticipant = participants[i];
            if (_reportingParticipant.getPayoutDistributionHash() != winningPayoutDistributionHash) {
                _reportingParticipant.liquidateLosing();
            }
        }

        IReputationToken _reputationToken = getReputationToken();

        // Now redistribute REP. We start at 1 since the designated/initial reporters do not get redistributed losses
        for (uint8 j = 1; j < participants.length; j++) {
            _reportingParticipant = participants[j];
            if (_reportingParticipant.getPayoutDistributionHash() == winningPayoutDistributionHash) {
                _reputationToken.transfer(_reportingParticipant, _reportingParticipant.getSize() / 2);
            }
        }
        return true;
    }

    function distributeNoShowBond(IInitialReporter _initialReporter) private returns (bool) {
        IReputationToken _reputationToken = getReputationToken();
        uint256 _repBalance = _reputationToken.balanceOf(this);
        // If the designated reporter showed up return the no show bond to the market creator. Otherwise it will be used as stake in the first report.
        if (msg.sender == _initialReporter.getDesignatedReporter()) {
            _reputationToken.transfer(owner, _repBalance);
        } else {
            _reputationToken.transfer(_initialReporter, _repBalance);
        }
        return true;
    }

    function getMarketCreatorSettlementFeeDivisor() public view returns (uint256) {
        return feeDivisor;
    }

    function distributeValidityBond() private returns (bool) {
        // If the market resolved to invalid the bond gets sent to the fee window. Otherwise it gets returned to the market creator mailbox.
        if (isInvalid()) {
            require(marketCreatorMailbox.call.value(validityBondAttoeth)());
        } else {
            require(feeWindow.call.value(validityBondAttoeth)());
        }
        return true;
    }

    function getOrCreateDisputeCrowdsourcer(bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) private returns (IDisputeCrowdsourcer) {
        IDisputeCrowdsourcer _crowdsourcer = IDisputeCrowdsourcer(crowdsourcers.getAsAddress(_payoutDistributionHash));
        if (_crowdsourcer == address(0)) {
            uint256 _size = 2 * getTotalStake() - 3 * getStakeInOutcome(_payoutDistributionHash);
            DisputeCrowdsourcerFactory _disputeCrowdsourcerFactory = DisputeCrowdsourcerFactory(controller.lookup("DisputeCrowdsourcerFactory"));
            _crowdsourcer = _disputeCrowdsourcerFactory.createDisputeCrowdsourcer(controller, this, _size, _payoutDistributionHash, _payoutNumerators, _invalid);
        }
        return _crowdsourcer;
    }

    function fork() private {
        universe.fork();
        for (uint8 i = 0; i < participants.length; ++i) {
            participants[i].fork();
        }
    }

    function migrateThroughOneFork() public {
        // only proceed if the forking market is finalized
        require(feeWindow.isForkingMarketFinalized());

        bytes32 _winningForkPayoutDistributionHash = _currentUniverse.getForkingMarket().getWinningPayoutDistributionHash();
        IUniverse _currentUniverse = universe;
        IUniverse _destinationUniverse = _currentUniverse.getChildUniverse(_winningForkPayoutDistributionHash);
        // follow the forking market to its universe
        _destinationUniverse.addMarketTo();
        _currentUniverse.removeMarketFrom();
        universe = _destinationUniverse;
        // reset state back to Initial Reporter
        feeWindow = IFeeWindow(0);
        IInitialReporter _initialParticipant = getInitialReporter();
        for (uint8 i = 1; i < participants.length; ++i) {
            IDisputeCrowdsourcer(participants[i]).disavow();
        }
        delete participants;
        participants.push(_initialParticipant);
        _initialParticipant.resetReportTimestamp();
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this);
    }

    function getTotalStake() public view returns (uint256) {
        uint256 _sum;
        for (uint8 i = 0; i < participants.length; ++i) {
            _sum += participants[i].getStake();
        }
        return _sum;
    }

    function getStakeInOutcome(bytes32 _payoutDistributionHash) public view returns (uint256) {
        uint256 _sum;
        for (uint8 i = 0; i < participants.length; ++i) {
            if (participants[i].getPayoutDistributionHash() != _payoutDistributionHash) {
                continue;
            }
            _sum += participants[i].getStake();
        }
        return _sum;
    }

    function getTypeName() public view returns (bytes32) {
        return "Market";
    }

    function getForkingMarket() public view returns (IMarket) {
        return universe.getForkingMarket();
    }

    function getWinningPayoutDistributionHash() public view returns (bytes32) {
        return winningPayoutDistributionHash;
    }

    function isFinalized() public view returns (bool) {
        return winningPayoutDistributionHash != bytes32(0);
    }

    function designatedReporterShowed() public view returns (bool) {
        return getInitialReporter().designatedReporterShowed();
    }

    function designatedReporterWasCorrect() public view returns (bool) {
        return getInitialReporter().designatedReporterWasCorrect();
    }

    function getEndTime() public view returns (uint256) {
        return endTime;
    }

    function getMarketCreatorMailbox() public view returns (IMailbox) {
        return marketCreatorMailbox;
    }

    function isInvalid() public view returns (bool) {
        require(isFinalized());
        return getWinningReportingParticipant().isInvalid();
    }

    function getInitialReporter() private view returns (IInitialReporter) {
        return IInitialReporter(participants[0]);
    }

    function getWinningReportingParticipant() private view returns (IReportingParticipant) {
        require(isFinalized());
        return participants[participants.length-1];
    }

    function getWinningPayoutNumerator(uint8 _outcome) public view returns (uint256) {
        require(isFinalized());
        return getWinningReportingParticipant().getPayoutNumerator(_outcome);
    }

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function getFeeWindow() public view returns (IFeeWindow) {
        return feeWindow;
    }

    function getFinalizationTime() public view returns (uint256) {
        return finalizationTime;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return universe.getReputationToken();
    }

    function getNumberOfOutcomes() public view returns (uint8) {
        return numOutcomes;
    }

    function getNumTicks() public view returns (uint256) {
        return numTicks;
    }

    function getDenominationToken() public view returns (ICash) {
        return cash;
    }

    function getShareToken(uint8 _outcome) public view returns (IShareToken) {
        return shareTokens[_outcome];
    }

    function derivePayoutDistributionHash(uint256[] _payoutNumerators, bool _invalid) public view returns (bytes32) {
        uint256 _sum = 0;
        uint256 _previousValue = _payoutNumerators[0];
        for (uint8 i = 0; i < _payoutNumerators.length; i++) {
            uint256 _value = _payoutNumerators[i];
            // This cannot reasonably exceed uint256 max value as it would require an invalid numTicks
            _sum += _value;
            require(!_invalid || _value == _previousValue);
            _previousValue = _value;
        }
        require(_sum == numTicks);
        return keccak256(_payoutNumerators, _invalid);
    }

    function isContainerForShareToken(IShareToken _shadyShareToken) public view returns (bool) {
        return getShareToken(_shadyShareToken.getOutcome()) == _shadyShareToken;
    }

    function isContainerForReportingParticipant(IReportingParticipant _shadyReportingParticipant) public view returns (bool) {
        if (IReportingParticipant(crowdsourcers.getAsAddress(_shadyReportingParticipant.getPayoutDistributionHash())) == _shadyReportingParticipant) {
            return true;
        }
        for (uint8 i = 0; i < participants.length; i++) {
            if (_shadyReportingParticipant == participants[i]) {
                return true;
            }
        }
        return false;
    }

    // Markets hold the initial fees paid by the creator in ETH and REP, so we dissallow ETH and REP extraction by the controller
    function getProtectedTokens() internal returns (address[] memory) {
        address[] memory _protectedTokens = new address[](numOutcomes + 3);
        for (uint8 i = 0; i < numOutcomes; i++) {
            _protectedTokens[i] = shareTokens[i];
        }
        // address(1) is the sentinel value for Ether extraction
        _protectedTokens[numOutcomes] = address(1);
        _protectedTokens[numOutcomes + 1] = feeWindow.getReputationToken();
        _protectedTokens[numOutcomes + 2] = cash;
        return _protectedTokens;
    }
}

pragma solidity 0.4.24;

import 'reporting/IMarket.sol';
import 'Controlled.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/Ownable.sol';
import 'libraries/collections/Map.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingParticipant.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IV2ReputationToken.sol';
import 'factories/DisputeCrowdsourcerFactory.sol';
import 'trading/ICash.sol';
import 'trading/IShareToken.sol';
import 'factories/ShareTokenFactory.sol';
import 'factories/InitialReporterFactory.sol';
import 'factories/MapFactory.sol';
import 'libraries/token/ERC20Basic.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/SafeMathInt256.sol';
import 'factories/MailboxFactory.sol';
import 'reporting/IMailbox.sol';
import 'reporting/Reporting.sol';
import 'reporting/IInitialReporter.sol';


contract Market is Controlled, ITyped, Initializable, Ownable, IMarket {
    using SafeMathUint256 for uint256;
    using SafeMathInt256 for int256;

    // Constants
    uint256 private constant MAX_FEE_PER_ETH_IN_ATTOETH = 15 * 10**16; // 15%
    uint256 private constant APPROVAL_AMOUNT = 2 ** 256 - 1;
    address private constant NULL_ADDRESS = address(0);
    uint256 private constant MIN_OUTCOMES = 3; // Includes INVALID
    uint256 private constant MAX_OUTCOMES = 8;

    // Contract Refs
    IUniverse private universe;
    IDisputeWindow private disputeWindow;
    ICash private cash;

    // Attributes
    uint256 private numTicks;
    uint256 private feeDivisor;
    uint256 private endTime;
    uint256 private numOutcomes;
    bytes32 private winningPayoutDistributionHash;
    uint256 private validityBondAttoEth;
    IMailbox private marketCreatorMailbox;
    uint256 private finalizationTime;
    uint256 private noShowBond;
    bool private disputePacingOn;
    address private noShowBondOwner;

    // Collections
    IReportingParticipant[] public participants;
    Map public crowdsourcers;
    IShareToken[] private shareTokens;

    function initialize(IUniverse _universe, uint256 _endTime, uint256 _feePerEthInAttoEth, address _designatedReporterAddress, address _creator, uint256 _numOutcomes, uint256 _numTicks) public payable beforeInitialized returns (bool _success) {
        endInitialization();
        _numOutcomes += 1; // The INVALID outcome is always first
        require(MIN_OUTCOMES <= _numOutcomes && _numOutcomes <= MAX_OUTCOMES);
        require(_designatedReporterAddress != NULL_ADDRESS);
        require((_numTicks >= _numOutcomes));
        require(_feePerEthInAttoEth <= MAX_FEE_PER_ETH_IN_ATTOETH);
        require(_creator != NULL_ADDRESS);
        uint256 _timestamp = controller.getTimestamp();
        require(_timestamp < _endTime);
        require(_endTime < _timestamp + Reporting.getMaximumMarketDuration());
        universe = _universe;
        require(!universe.isForking());
        cash = ICash(controller.lookup("Cash"));
        owner = _creator;
        noShowBondOwner = owner;
        assessFees();
        endTime = _endTime;
        numOutcomes = _numOutcomes;
        numTicks = _numTicks;
        feeDivisor = _feePerEthInAttoEth == 0 ? 0 : 1 ether / _feePerEthInAttoEth;
        InitialReporterFactory _initialReporterFactory = InitialReporterFactory(controller.lookup("InitialReporterFactory"));
        participants.push(_initialReporterFactory.createInitialReporter(controller, this, _designatedReporterAddress));
        marketCreatorMailbox = MailboxFactory(controller.lookup("MailboxFactory")).createMailbox(controller, owner, this);
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this);
        for (uint256 _outcome = 0; _outcome < numOutcomes; _outcome++) {
            shareTokens.push(createShareToken(_outcome));
        }
        approveSpenders();
        return true;
    }

    function assessFees() private returns (bool) {
        noShowBond = universe.getOrCacheDesignatedReportNoShowBond();
        require(getReputationToken().balanceOf(this) >= noShowBond);
        require(msg.value >= universe.getOrCacheValidityBond());
        validityBondAttoEth = msg.value;
        return true;
    }

    function createShareToken(uint256 _outcome) private returns (IShareToken) {
        return ShareTokenFactory(controller.lookup("ShareTokenFactory")).createShareToken(controller, this, _outcome);
    }

    // This will need to be called manually for each open market if a spender contract is updated
    function approveSpenders() public returns (bool) {
        bytes32[4] memory _names = [bytes32("CancelOrder"), bytes32("CompleteSets"), bytes32("FillOrder"), bytes32("ClaimTradingProceeds")];
        for (uint256 i = 0; i < _names.length; i++) {
            require(cash.approve(controller.lookup(_names[i]), APPROVAL_AMOUNT));
        }
        for (uint256 j = 0; j < numOutcomes; j++) {
            require(shareTokens[j].approve(controller.lookup("FillOrder"), APPROVAL_AMOUNT));
        }
        return true;
    }

    function doInitialReport(uint256[] _payoutNumerators, string _description) public returns (bool) {
        doInitialReportInternal(msg.sender, _payoutNumerators, _description);
        return true;
    }

    function doInitialReportInternal(address _reporter, uint256[] _payoutNumerators, string _description) private returns (bool) {
        require(!universe.isForking());
        IInitialReporter _initialReporter = getInitialReporter();
        uint256 _timestamp = controller.getTimestamp();
        require(_timestamp > endTime);
        uint256 _initialReportStake = distributeInitialReportingRep(_reporter, _initialReporter);
        // The derive call will validate that an Invalid report is entirely paid out on the Invalid outcome
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        disputeWindow = universe.getOrCreateNextDisputeWindow();
        _initialReporter.report(_reporter, _payoutDistributionHash, _payoutNumerators, _initialReportStake);
        controller.getAugur().logInitialReportSubmitted(universe, _reporter, this, _initialReportStake, _initialReporter.designatedReporterShowed(), _payoutNumerators, _description);
        return true;
    }

    function distributeInitialReportingRep(address _reporter, IInitialReporter _initialReporter) private returns (uint256) {
        IV2ReputationToken _reputationToken = getReputationToken();
        uint256 _initialReportStake = noShowBond;
        // If the designated reporter showed up return the no show bond to the bond owner. Otherwise it will be used as stake in the first report.
        if (_reporter == _initialReporter.getDesignatedReporter()) {
            require(_reputationToken.transfer(noShowBondOwner, _initialReportStake));
            _initialReportStake = universe.getOrCacheDesignatedReportStake();
            _reputationToken.trustedMarketTransfer(_reporter, _initialReporter, _initialReportStake);
        } else {
            require(_reputationToken.transfer(_initialReporter, _initialReportStake));
        }
        noShowBond = 0;
        return _initialReportStake;
    }

    function contribute(uint256[] _payoutNumerators, uint256 _amount, string _description) public returns (bool) {
        require(getInitialReporter().getReportTimestamp() != 0);
        if (disputePacingOn) {
            require(disputeWindow.isActive());
        } else {
            require(!disputeWindow.isOver());
        }
        require(!universe.isForking());
        // The derive call will validate that an Invalid report is entirely paid out on the Invalid outcome
        bytes32 _payoutDistributionHash = derivePayoutDistributionHash(_payoutNumerators);
        require(_payoutDistributionHash != getWinningReportingParticipant().getPayoutDistributionHash());
        IDisputeCrowdsourcer _crowdsourcer = getOrCreateDisputeCrowdsourcer(_payoutDistributionHash, _payoutNumerators);
        uint256 _actualAmount = _crowdsourcer.contribute(msg.sender, _amount);
        controller.getAugur().logDisputeCrowdsourcerContribution(universe, msg.sender, this, _crowdsourcer, _actualAmount, _description);
        if (_crowdsourcer.totalSupply() == _crowdsourcer.getSize()) {
            finishedCrowdsourcingDisputeBond(_crowdsourcer);
        }
        return true;
    }

    function finishedCrowdsourcingDisputeBond(IReportingParticipant _reportingParticipant) private returns (bool) {
        participants.push(_reportingParticipant);
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this); // disavow other crowdsourcers
        uint256 _crowdsourcerSize = IDisputeCrowdsourcer(_reportingParticipant).getSize();
        if (_crowdsourcerSize >= universe.getDisputeThresholdForFork()) {
            universe.fork();
        } else {
            if (_crowdsourcerSize >= universe.getDisputeThresholdForDisputePacing()) {
                disputePacingOn = true;
            }
            disputeWindow = universe.getOrCreateNextDisputeWindow();
        }
        controller.getAugur().logDisputeCrowdsourcerCompleted(universe, this, _reportingParticipant);
        return true;
    }

    function finalize() public returns (bool) {
        if (universe.getForkingMarket() == this) {
            return finalizeFork();
        }

        require(winningPayoutDistributionHash == bytes32(0));

        require(getInitialReporter().getReportTimestamp() != 0);
        require(disputeWindow.isOver());
        require(!universe.isForking());
        winningPayoutDistributionHash = participants[participants.length-1].getPayoutDistributionHash();
        disputeWindow.onMarketFinalized();
        universe.decrementOpenInterestFromMarket(shareTokens[0].totalSupply().mul(numTicks));
        redistributeLosingReputation();
        distributeValidityBond();
        finalizationTime = controller.getTimestamp();
        controller.getAugur().logMarketFinalized(universe);
        return true;
    }

    function finalizeFork() public returns (bool) {
        require(universe.getForkingMarket() == this);
        require(winningPayoutDistributionHash == bytes32(0));
        IUniverse _winningUniverse = universe.getWinningChildUniverse();
        winningPayoutDistributionHash = _winningUniverse.getParentPayoutDistributionHash();
        finalizationTime = controller.getTimestamp();
        controller.getAugur().logMarketFinalized(universe);
        return true;
    }

    function redistributeLosingReputation() private returns (bool) {
        // If no disputes occured early exit
        if (participants.length == 1) {
            return true;
        }

        IReportingParticipant _reportingParticipant;

        // Initial pass is to liquidate losers so we have sufficient REP to pay the winners. Participants is implicitly bounded by the floor of the initial report REP cost to be no more than 21
        for (uint256 i = 0; i < participants.length; i++) {
            _reportingParticipant = participants[i];
            if (_reportingParticipant.getPayoutDistributionHash() != winningPayoutDistributionHash) {
                _reportingParticipant.liquidateLosing();
            }
        }

        IV2ReputationToken _reputationToken = getReputationToken();

        // Now redistribute REP. Participants is implicitly bounded by the floor of the initial report REP cost to be no more than 21.
        for (uint256 j = 0; j < participants.length; j++) {
            _reportingParticipant = participants[j];
            if (_reportingParticipant.getPayoutDistributionHash() == winningPayoutDistributionHash) {
                require(_reputationToken.transfer(_reportingParticipant, _reportingParticipant.getSize().mul(2) / 5));
            }
        }

        // We burn 20% of the REP to prevent griefing attacks which rely on getting back lost REP
        _reputationToken.burnForMarket(_reputationToken.balanceOf(this));
        return true;
    }

    function getMarketCreatorSettlementFeeDivisor() public view returns (uint256) {
        return feeDivisor;
    }

    function deriveMarketCreatorFeeAmount(uint256 _amount) public view returns (uint256) {
        if (feeDivisor == 0) {
            return 0;
        }
        return _amount / feeDivisor;
    }

    function distributeValidityBond() private returns (bool) {
        // If the market resolved to invalid the bond gets sent to the auction. Otherwise it gets returned to the market creator mailbox.
        if (!isInvalid()) {
            marketCreatorMailbox.depositEther.value(validityBondAttoEth)();
        } else {
            cash.depositEtherFor.value(validityBondAttoEth)(universe.getAuction());
        }
        return true;
    }

    function getOrCreateDisputeCrowdsourcer(bytes32 _payoutDistributionHash, uint256[] _payoutNumerators) private returns (IDisputeCrowdsourcer) {
        IDisputeCrowdsourcer _crowdsourcer = IDisputeCrowdsourcer(crowdsourcers.getAsAddressOrZero(_payoutDistributionHash));
        if (_crowdsourcer == IDisputeCrowdsourcer(0)) {
            uint256 _size = getParticipantStake().mul(2).sub(getStakeInOutcome(_payoutDistributionHash).mul(3));
            DisputeCrowdsourcerFactory _disputeCrowdsourcerFactory = DisputeCrowdsourcerFactory(controller.lookup("DisputeCrowdsourcerFactory"));
            _crowdsourcer = _disputeCrowdsourcerFactory.createDisputeCrowdsourcer(controller, this, _size, _payoutDistributionHash, _payoutNumerators);
            crowdsourcers.add(_payoutDistributionHash, address(_crowdsourcer));
            controller.getAugur().disputeCrowdsourcerCreated(universe, this, _crowdsourcer, _payoutNumerators, _size);
        }
        return _crowdsourcer;
    }

    function migrateThroughOneFork(uint256[] _payoutNumerators, string _description) public returns (bool) {
        // only proceed if the forking market is finalized
        IMarket _forkingMarket = universe.getForkingMarket();
        require(_forkingMarket.isFinalized());
        require(!isFinalized());

        disavowCrowdsourcers();

        IUniverse _currentUniverse = universe;
        bytes32 _winningForkPayoutDistributionHash = _forkingMarket.getWinningPayoutDistributionHash();
        IUniverse _destinationUniverse = _currentUniverse.getChildUniverse(_winningForkPayoutDistributionHash);

        uint256 _marketOI = shareTokens[0].totalSupply().mul(numTicks);

        universe.decrementOpenInterestFromMarket(_marketOI);

        // follow the forking market to its universe
        if (disputeWindow != IDisputeWindow(0)) {
            disputeWindow = _destinationUniverse.getOrCreateNextDisputeWindow();
        }
        _destinationUniverse.addMarketTo();
        _currentUniverse.removeMarketFrom();
        universe = _destinationUniverse;

        universe.incrementOpenInterestFromMarket(_marketOI);

        // Pay the No Show REP bond
        noShowBond = universe.getOrCacheDesignatedReportStake();
        noShowBondOwner = msg.sender;
        getReputationToken().trustedMarketTransfer(noShowBondOwner, this, noShowBond);

        // Update the Initial Reporter
        IInitialReporter _initialReporter = getInitialReporter();
        _initialReporter.migrateToNewUniverse(msg.sender);

        // If the market is past expiration use the reporting data to make an initial report
        uint256 _timestamp = controller.getTimestamp();
        if (_timestamp > endTime) {
            doInitialReportInternal(msg.sender, _payoutNumerators, _description);
        }

        return true;
    }

    function disavowCrowdsourcers() public returns (bool) {
        require(universe.isForking());
        IMarket _forkingMarket = getForkingMarket();
        require(_forkingMarket != this);
        require(!isFinalized());
        IInitialReporter _initialParticipant = getInitialReporter();
        // Early out if already disavowed or nothing to disavow
        if (_initialParticipant.getReportTimestamp() == 0) {
            return true;
        }
        delete participants;
        participants.push(_initialParticipant);
        // Send REP from the no show bond back to the address that placed it. If a report has been made tell the InitialReporter to return that REP and reset
        if (noShowBond > 0) {
            IV2ReputationToken _reputationToken = getReputationToken();
            require(_reputationToken.transfer(noShowBondOwner, noShowBond));
            noShowBond = 0;
        } else {
            _initialParticipant.returnRepFromDisavow();
        }
        crowdsourcers = MapFactory(controller.lookup("MapFactory")).createMap(controller, this);
        controller.getAugur().logMarketParticipantsDisavowed(universe);
        return true;
    }

    function getParticipantStake() public view returns (uint256) {
        uint256 _sum;
        // Participants is implicitly bounded by the floor of the initial report REP cost to be no more than 21
        for (uint256 i = 0; i < participants.length; ++i) {
            _sum += participants[i].getStake();
        }
        return _sum;
    }

    function getStakeInOutcome(bytes32 _payoutDistributionHash) public view returns (uint256) {
        uint256 _sum;
        // Participants is implicitly bounded by the floor of the initial report REP cost to be no more than 21
        for (uint256 i = 0; i < participants.length; ++i) {
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

    function getDesignatedReporter() public view returns (address) {
        return getInitialReporter().getDesignatedReporter();
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
        return getWinningReportingParticipant().getPayoutNumerator(0) > 0;
    }

    function getInitialReporter() public view returns (IInitialReporter) {
        return IInitialReporter(participants[0]);
    }

    function getInitialReporterAddress() public view returns (address) {
        return address(participants[0]);
    }

    function getReportingParticipant(uint256 _index) public view returns (IReportingParticipant) {
        return participants[_index];
    }

    function getCrowdsourcer(bytes32 _payoutDistributionHash) public view returns (IDisputeCrowdsourcer) {
        return  IDisputeCrowdsourcer(crowdsourcers.getAsAddressOrZero(_payoutDistributionHash));
    }

    function getWinningReportingParticipant() public view returns (IReportingParticipant) {
        return participants[participants.length-1];
    }

    function getWinningPayoutNumerator(uint256 _outcome) public view returns (uint256) {
        require(isFinalized());
        return getWinningReportingParticipant().getPayoutNumerator(_outcome);
    }

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function getDisputeWindow() public view returns (IDisputeWindow) {
        return disputeWindow;
    }

    function getFinalizationTime() public view returns (uint256) {
        return finalizationTime;
    }

    function getReputationToken() public view returns (IV2ReputationToken) {
        return universe.getReputationToken();
    }

    function getNumberOfOutcomes() public view returns (uint256) {
        return numOutcomes;
    }

    function getNumTicks() public view returns (uint256) {
        return numTicks;
    }

    function getDenominationToken() public view returns (ICash) {
        return cash;
    }

    function getShareToken(uint256 _outcome) public view returns (IShareToken) {
        return shareTokens[_outcome];
    }

    function getDesignatedReportingEndTime() public view returns (uint256) {
        return endTime.add(Reporting.getDesignatedReportingDurationSeconds());
    }

    function getNumParticipants() public view returns (uint256) {
        return participants.length;
    }

    function getValidityBondAttoEth() public view returns (uint256) {
        return validityBondAttoEth;
    }

    function getDisputePacingOn() public view returns (bool) {
        return disputePacingOn;
    }

    function derivePayoutDistributionHash(uint256[] _payoutNumerators) public view returns (bytes32) {
        uint256 _sum = 0;
        uint256 _previousValue = _payoutNumerators[0];
        require(_payoutNumerators[0] == 0 || _payoutNumerators[0] == numTicks);
        require(_payoutNumerators.length == numOutcomes);
        for (uint256 i = 0; i < _payoutNumerators.length; i++) {
            uint256 _value = _payoutNumerators[i];
            _sum = _sum.add(_value);
            _previousValue = _value;
        }
        require(_sum == numTicks);
        return keccak256(abi.encodePacked(_payoutNumerators));
    }

    function isContainerForShareToken(IShareToken _shadyShareToken) public view returns (bool) {
        return getShareToken(_shadyShareToken.getOutcome()) == _shadyShareToken;
    }

    function isContainerForReportingParticipant(IReportingParticipant _shadyReportingParticipant) public view returns (bool) {
        if (crowdsourcers.getAsAddressOrZero(_shadyReportingParticipant.getPayoutDistributionHash()) == address(_shadyReportingParticipant)) {
            return true;
        }
        // Participants is implicitly bounded by the floor of the initial report REP cost to be no more than 21
        for (uint256 i = 0; i < participants.length; i++) {
            if (_shadyReportingParticipant == participants[i]) {
                return true;
            }
        }
        return false;
    }

    function onTransferOwnership(address _owner, address _newOwner) internal returns (bool) {
        controller.getAugur().logMarketTransferred(getUniverse(), _owner, _newOwner);
        return true;
    }

    function assertBalances() public view returns (bool) {
        // Escrowed funds for open orders
        uint256 _expectedBalance = IOrders(controller.lookup("Orders")).getTotalEscrowed(this);
        // Market Open Interest. If we're finalized we need actually calculate the value
        if (isFinalized()) {
            IReportingParticipant _winningReportingPartcipant = getWinningReportingParticipant();
            for (uint256 i = 0; i < numOutcomes; i++) {
                _expectedBalance = _expectedBalance.add(shareTokens[i].totalSupply().mul(_winningReportingPartcipant.getPayoutNumerator(i)));
            }
        } else {
            _expectedBalance = _expectedBalance.add(shareTokens[0].totalSupply().mul(numTicks));
        }

        assert(cash.balanceOf(this) >= _expectedBalance);
        return true;
    }
}

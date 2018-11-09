pragma solidity 0.4.24;

import 'Controlled.sol';
import 'IAugur.sol';
import 'libraries/token/ERC20.sol';
import 'factories/UniverseFactory.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IDisputeWindow.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingParticipant.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IInitialReporter.sol';
import 'reporting/IMailbox.sol';
import 'trading/IShareToken.sol';
import 'trading/Order.sol';
import 'reporting/IAuction.sol';
import 'reporting/IAuctionToken.sol';


// Centralized approval authority and event emissions
contract Augur is Controlled, IAugur {

    enum TokenType{
        ReputationToken,
        ShareToken,
        DisputeCrowdsourcer,
        FeeWindow, // No longer a valid type but here for backward compat with Augur Node processing
        FeeToken, // No longer a valid type but here for backward compat with Augur Node processing
        AuctionToken
    }

    event MarketCreated(bytes32 indexed topic, string description, string extraInfo, address indexed universe, address market, address indexed marketCreator, bytes32[] outcomes, uint256 marketCreationFee, int256 minPrice, int256 maxPrice, IMarket.MarketType marketType);
    event InitialReportSubmitted(address indexed universe, address indexed reporter, address indexed market, uint256 amountStaked, bool isDesignatedReporter, uint256[] payoutNumerators, string description);
    event DisputeCrowdsourcerCreated(address indexed universe, address indexed market, address disputeCrowdsourcer, uint256[] payoutNumerators, uint256 size);
    event DisputeCrowdsourcerContribution(address indexed universe, address indexed reporter, address indexed market, address disputeCrowdsourcer, uint256 amountStaked, string description);
    event DisputeCrowdsourcerCompleted(address indexed universe, address indexed market, address disputeCrowdsourcer);
    event InitialReporterRedeemed(address indexed universe, address indexed reporter, address indexed market, uint256 amountRedeemed, uint256 repReceived, uint256[] payoutNumerators);
    event DisputeCrowdsourcerRedeemed(address indexed universe, address indexed reporter, address indexed market, address disputeCrowdsourcer, uint256 amountRedeemed, uint256 repReceived, uint256[] payoutNumerators);
    event ReportingParticipantDisavowed(address indexed universe, address indexed market, address reportingParticipant);
    event MarketParticipantsDisavowed(address indexed universe, address indexed market);
    event MarketFinalized(address indexed universe, address indexed market);
    event MarketMigrated(address indexed market, address indexed originalUniverse, address indexed newUniverse);
    event UniverseForked(address indexed universe);
    event UniverseCreated(address indexed parentUniverse, address indexed childUniverse, uint256[] payoutNumerators);
    event OrderCanceled(address indexed universe, address indexed shareToken, address indexed sender, bytes32 orderId, Order.Types orderType, uint256 tokenRefund, uint256 sharesRefund);
    // The ordering here is to match functions higher in the call chain to avoid stack depth issues
    event OrderCreated(Order.Types orderType, uint256 amount, uint256 price, address indexed creator, uint256 moneyEscrowed, uint256 sharesEscrowed, bytes32 tradeGroupId, bytes32 orderId, address indexed universe, address indexed shareToken);
    event OrderFilled(address indexed universe, address indexed shareToken, address filler, bytes32 orderId, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 marketCreatorFees, uint256 reporterFees, uint256 amountFilled, bytes32 tradeGroupId);
    event CompleteSetsPurchased(address indexed universe, address indexed market, address indexed account, uint256 numCompleteSets);
    event CompleteSetsSold(address indexed universe, address indexed market, address indexed account, uint256 numCompleteSets);
    event TradingProceedsClaimed(address indexed universe, address indexed shareToken, address indexed sender, address market, uint256 numShares, uint256 numPayoutTokens, uint256 finalTokenBalance);
    event TokensTransferred(address indexed universe, address indexed token, address indexed from, address to, uint256 value, TokenType tokenType, address market);
    event TokensMinted(address indexed universe, address indexed token, address indexed target, uint256 amount, TokenType tokenType, address market);
    event TokensBurned(address indexed universe, address indexed token, address indexed target, uint256 amount, TokenType tokenType, address market);
    event DisputeWindowCreated(address indexed universe, address disputeWindow, uint256 startTime, uint256 endTime, uint256 id);
    event InitialReporterTransferred(address indexed universe, address indexed market, address from, address to);
    event MarketTransferred(address indexed universe, address indexed market, address from, address to);
    event MarketMailboxTransferred(address indexed universe, address indexed market, address indexed mailbox, address from, address to);
    event EscapeHatchChanged(bool isOn);
    event TimestampSet(uint256 newTimestamp);

    mapping(address => bool) private universes;
    mapping(address => bool) private crowdsourcers;
    mapping(address => bool) private shareTokens;
    mapping(address => bool) private auctionTokens;

    //
    // Universe
    //

    function createGenesisUniverse() public returns (IUniverse) {
        return createUniverse(IUniverse(0), bytes32(0), new uint256[](0));
    }

    function createChildUniverse(bytes32 _parentPayoutDistributionHash, uint256[] _parentPayoutNumerators) public returns (IUniverse) {
        IUniverse _parentUniverse = IUniverse(msg.sender);
        require(isKnownUniverse(_parentUniverse));
        return createUniverse(_parentUniverse, _parentPayoutDistributionHash, _parentPayoutNumerators);
    }

    function createUniverse(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash, uint256[] _parentPayoutNumerators) private returns (IUniverse) {
        UniverseFactory _universeFactory = UniverseFactory(controller.lookup("UniverseFactory"));
        IUniverse _newUniverse = _universeFactory.createUniverse(controller, _parentUniverse, _parentPayoutDistributionHash);
        universes[_newUniverse] = true;
        emit UniverseCreated(_parentUniverse, _newUniverse, _parentPayoutNumerators);
        return _newUniverse;
    }

    function isKnownUniverse(IUniverse _universe) public view returns (bool) {
        return universes[_universe];
    }

    //
    // Crowdsourcers
    //

    function isKnownCrowdsourcer(IDisputeCrowdsourcer _crowdsourcer) public view returns (bool) {
        return crowdsourcers[_crowdsourcer];
    }

    function disputeCrowdsourcerCreated(IUniverse _universe, address _market, address _disputeCrowdsourcer, uint256[] _payoutNumerators, uint256 _size) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        crowdsourcers[_disputeCrowdsourcer] = true;
        emit DisputeCrowdsourcerCreated(_universe, _market, _disputeCrowdsourcer, _payoutNumerators, _size);
        return true;
    }

    //
    // Share Tokens
    //
    function recordMarketShareTokens(IMarket _market) private returns (bool) {
        uint256 _numOutcomes = _market.getNumberOfOutcomes();
        for (uint256 _outcome = 0; _outcome < _numOutcomes; _outcome++) {
            shareTokens[_market.getShareToken(_outcome)] = true;
        }
    }

    function isKnownShareToken(IShareToken _token) public view returns (bool) {
        return shareTokens[_token];
    }

    //
    // Auction Tokens
    //
    function recordAuctionTokens(IUniverse _universe) public returns (bool) {
        require(isKnownUniverse(_universe));
        IAuction _auction = _universe.getAuction();
        IAuctionToken _ethAuctionToken = _auction.ethAuctionToken();
        IAuctionToken _repAuctionToken = _auction.repAuctionToken();
        if (_ethAuctionToken != IAuctionToken(0)) {
            auctionTokens[_ethAuctionToken] = true;
        }
        if (_repAuctionToken != IAuctionToken(0)) {
            auctionTokens[_repAuctionToken] = true;
        }
    }

    function isKnownAuctionToken(IAuctionToken _token) public view returns (bool) {
        return auctionTokens[_token];
    }

    //
    // Transfer
    //

    function trustedTransfer(ERC20 _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        require(_token.transferFrom(_from, _to, _amount));
        return true;
    }

    //
    // Logging
    //

    // This signature is intended for the categorical market creation. We use two signatures for the same event because of stack depth issues which can be circumvented by maintaining order of paramaters
    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, IMarket _market, address _marketCreator, bytes32[] _outcomes, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe == IUniverse(msg.sender));
        recordMarketShareTokens(_market);
        emit MarketCreated(_topic, _description, _extraInfo, _universe, _market, _marketCreator, _outcomes, _universe.getOrCacheMarketCreationCost(), _minPrice, _maxPrice, _marketType);
        return true;
    }

    // This signature is intended for yesNo and scalar market creation. See function comment above for explanation.
    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, IMarket _market, address _marketCreator, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe == IUniverse(msg.sender));
        recordMarketShareTokens(_market);
        emit MarketCreated(_topic, _description, _extraInfo, _universe, _market, _marketCreator, new bytes32[](0), _universe.getOrCacheMarketCreationCost(), _minPrice, _maxPrice, _marketType);
        return true;
    }

    function logInitialReportSubmitted(IUniverse _universe, address _reporter, address _market, uint256 _amountStaked, bool _isDesignatedReporter, uint256[] _payoutNumerators, string _description) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        emit InitialReportSubmitted(_universe, _reporter, _market, _amountStaked, _isDesignatedReporter, _payoutNumerators, _description);
        return true;
    }

    function logDisputeCrowdsourcerContribution(IUniverse _universe, address _reporter, address _market, address _disputeCrowdsourcer, uint256 _amountStaked, string _description) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        emit DisputeCrowdsourcerContribution(_universe, _reporter, _market, _disputeCrowdsourcer, _amountStaked, _description);
        return true;
    }

    function logDisputeCrowdsourcerCompleted(IUniverse _universe, address _market, address _disputeCrowdsourcer) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        emit DisputeCrowdsourcerCompleted(_universe, _market, _disputeCrowdsourcer);
        return true;
    }

    function logInitialReporterRedeemed(IUniverse _universe, address _reporter, address _market, uint256 _amountRedeemed, uint256 _repReceived, uint256[] _payoutNumerators) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        emit InitialReporterRedeemed(_universe, _reporter, _market, _amountRedeemed, _repReceived, _payoutNumerators);
        return true;
    }

    function logDisputeCrowdsourcerRedeemed(IUniverse _universe, address _reporter, address _market, uint256 _amountRedeemed, uint256 _repReceived, uint256[] _payoutNumerators) public returns (bool) {
        IDisputeCrowdsourcer _disputeCrowdsourcer = IDisputeCrowdsourcer(msg.sender);
        require(isKnownCrowdsourcer(_disputeCrowdsourcer));
        emit DisputeCrowdsourcerRedeemed(_universe, _reporter, _market, _disputeCrowdsourcer, _amountRedeemed, _repReceived, _payoutNumerators);
        return true;
    }

    function logReportingParticipantDisavowed(IUniverse _universe, IMarket _market) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        emit ReportingParticipantDisavowed(_universe, _market, msg.sender);
        return true;
    }

    function logMarketParticipantsDisavowed(IUniverse _universe) public returns (bool) {
        require(isKnownUniverse(_universe));
        IMarket _market = IMarket(msg.sender);
        require(_universe.isContainerForMarket(_market));
        emit MarketParticipantsDisavowed(_universe, _market);
        return true;
    }

    function logMarketFinalized(IUniverse _universe) public returns (bool) {
        require(isKnownUniverse(_universe));
        IMarket _market = IMarket(msg.sender);
        require(_universe.isContainerForMarket(_market));
        emit MarketFinalized(_universe, _market);
        return true;
    }

    function logMarketMigrated(IMarket _market, IUniverse _originalUniverse) public returns (bool) {
        IUniverse _newUniverse = IUniverse(msg.sender);
        require(isKnownUniverse(_newUniverse));
        emit MarketMigrated(_market, _originalUniverse, _newUniverse);
        return true;
    }

    function logOrderCanceled(IUniverse _universe, address _shareToken, address _sender, bytes32 _orderId, Order.Types _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public onlyWhitelistedCallers returns (bool) {
        emit OrderCanceled(_universe, _shareToken, _sender, _orderId, _orderType, _tokenRefund, _sharesRefund);
        return true;
    }

    function logOrderCreated(Order.Types _orderType, uint256 _amount, uint256 _price, address _creator, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _tradeGroupId, bytes32 _orderId, IUniverse _universe, address _shareToken) public onlyWhitelistedCallers returns (bool) {
        emit OrderCreated(_orderType, _amount, _price, _creator, _moneyEscrowed, _sharesEscrowed, _tradeGroupId, _orderId, _universe, _shareToken);
        return true;
    }

    function logOrderFilled(IUniverse _universe, address _shareToken, address _filler, bytes32 _orderId, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _marketCreatorFees, uint256 _reporterFees, uint256 _amountFilled, bytes32 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        emit OrderFilled(_universe, _shareToken, _filler, _orderId, _numCreatorShares, _numCreatorTokens, _numFillerShares, _numFillerTokens, _marketCreatorFees, _reporterFees, _amountFilled, _tradeGroupId);
        return true;
    }

    function logCompleteSetsPurchased(IUniverse _universe, IMarket _market, address _account, uint256 _numCompleteSets) public onlyWhitelistedCallers returns (bool) {
        emit CompleteSetsPurchased(_universe, _market, _account, _numCompleteSets);
        return true;
    }

    function logCompleteSetsSold(IUniverse _universe, IMarket _market, address _account, uint256 _numCompleteSets) public onlyWhitelistedCallers returns (bool) {
        emit CompleteSetsSold(_universe, _market, _account, _numCompleteSets);
        return true;
    }

    function logTradingProceedsClaimed(IUniverse _universe, address _shareToken, address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public onlyWhitelistedCallers returns (bool) {
        emit TradingProceedsClaimed(_universe, _shareToken, _sender, _market, _numShares, _numPayoutTokens, _finalTokenBalance);
        return true;
    }

    function logUniverseForked() public returns (bool) {
        require(universes[msg.sender]);
        emit UniverseForked(msg.sender);
        return true;
    }

    function logReputationTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        emit TokensTransferred(_universe, msg.sender, _from, _to, _value, TokenType.ReputationToken, 0);
        return true;
    }

    function logDisputeCrowdsourcerTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        IDisputeCrowdsourcer _disputeCrowdsourcer = IDisputeCrowdsourcer(msg.sender);
        require(isKnownCrowdsourcer(_disputeCrowdsourcer));
        emit TokensTransferred(_universe, msg.sender, _from, _to, _value, TokenType.DisputeCrowdsourcer, _disputeCrowdsourcer.getMarket());
        return true;
    }

    function logShareTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        IShareToken _shareToken = IShareToken(msg.sender);
        require(isKnownShareToken(_shareToken));
        emit TokensTransferred(_universe, msg.sender, _from, _to, _value, TokenType.ShareToken, _shareToken.getMarket());
        return true;
    }

    function logReputationTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        emit TokensBurned(_universe, msg.sender, _target, _amount, TokenType.ReputationToken, 0);
        return true;
    }

    function logReputationTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        emit TokensMinted(_universe, msg.sender, _target, _amount, TokenType.ReputationToken, 0);
        return true;
    }

    function logShareTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        IShareToken _shareToken = IShareToken(msg.sender);
        require(isKnownShareToken(_shareToken));
        emit TokensBurned(_universe, msg.sender, _target, _amount, TokenType.ShareToken, _shareToken.getMarket());
        return true;
    }

    function logShareTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        IShareToken _shareToken = IShareToken(msg.sender);
        require(isKnownShareToken(_shareToken));
        emit TokensMinted(_universe, msg.sender, _target, _amount, TokenType.ShareToken, _shareToken.getMarket());
        return true;
    }

    function logDisputeCrowdsourcerTokensBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        IDisputeCrowdsourcer _disputeCrowdsourcer = IDisputeCrowdsourcer(msg.sender);
        require(isKnownCrowdsourcer(_disputeCrowdsourcer));
        emit TokensBurned(_universe, msg.sender, _target, _amount, TokenType.DisputeCrowdsourcer, _disputeCrowdsourcer.getMarket());
        return true;
    }

    function logDisputeCrowdsourcerTokensMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        IDisputeCrowdsourcer _disputeCrowdsourcer = IDisputeCrowdsourcer(msg.sender);
        require(isKnownCrowdsourcer(_disputeCrowdsourcer));
        emit TokensMinted(_universe, msg.sender, _target, _amount, TokenType.DisputeCrowdsourcer, _disputeCrowdsourcer.getMarket());
        return true;
    }

    function logDisputeWindowCreated(IDisputeWindow _disputeWindow, uint256 _id) public returns (bool) {
        require(universes[msg.sender]);
        emit DisputeWindowCreated(msg.sender, _disputeWindow, _disputeWindow.getStartTime(), _disputeWindow.getEndTime(), _id);
        return true;
    }

    function logTimestampSet(uint256 _newTimestamp) public returns (bool) {
        require(msg.sender == controller.lookup("Time"));
        emit TimestampSet(_newTimestamp);
        return true;
    }

    function logInitialReporterTransferred(IUniverse _universe, IMarket _market, address _from, address _to) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(_market));
        require(msg.sender == _market.getInitialReporterAddress());
        emit InitialReporterTransferred(_universe, _market, _from, _to);
        return true;
    }

    function logMarketTransferred(IUniverse _universe, address _from, address _to) public returns (bool) {
        require(isKnownUniverse(_universe));
        IMarket _market = IMarket(msg.sender);
        require(_universe.isContainerForMarket(_market));
        emit MarketTransferred(_universe, _market, _from, _to);
        return true;
    }

    function logMarketMailboxTransferred(IUniverse _universe, IMarket _market, address _from, address _to) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(_market));
        require(IMailbox(msg.sender) == _market.getMarketCreatorMailbox());
        emit MarketMailboxTransferred(_universe, _market, msg.sender, _from, _to);
        return true;
    }

    function logAuctionTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownAuctionToken(IAuctionToken(msg.sender)));
        emit TokensTransferred(_universe, msg.sender, _from, _to, _value, TokenType.AuctionToken, 0);
        return true;
    }

    function logAuctionTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownAuctionToken(IAuctionToken(msg.sender)));
        emit TokensBurned(_universe, msg.sender, _target, _amount, TokenType.AuctionToken, 0);
        return true;
    }

    function logAuctionTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownAuctionToken(IAuctionToken(msg.sender)));
        emit TokensMinted(_universe, msg.sender, _target, _amount, TokenType.AuctionToken, 0);
        return true;
    }
}

pragma solidity 0.4.20;


import 'trading/IShareToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'reporting/IMarket.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockShareToken is DelegationTarget, ITyped, Initializable, MockVariableSupplyToken, IShareToken {

    string constant public name = "Shares";
    uint256 constant public decimals = 0;
    string constant public symbol = "SHARE";

    IMarket private initializeMarketValue;
    IMarket private setMarketValue;
    uint256 private initializeOutcomeValue;
    address private createSharesOwnerValue;
    uint256 private createSharesFxpValue;
    address private destroySharesOwnerValue;
    uint256 private destroySharesFxpValueValue;
    uint256 private setOutcomeValue;
    bool private setIsShareTokenValue;

    function getInitializeMarketValue() public returns(IMarket) {
        return initializeMarketValue;
    }

    function getInitializeOutcomeValue() public returns(uint256) {
        return initializeOutcomeValue;
    }

    function getCreateSharesOwner() public returns(address) {
        return createSharesOwnerValue;
    }

    function getCreateSharesFxpValue() public returns(uint256) {
        return createSharesFxpValue;
    }

    function getDestroySharesOwnerValue() public returns(address) {
        return destroySharesOwnerValue;
    }

    function getDestroySharesFxpValueValue() public returns(uint256) {
        return destroySharesFxpValueValue;
    }

    function setMarket(IMarket _market) public {
        setMarketValue = _market;
    }

    function setOutcome(uint256 _outcome) public {
        setOutcomeValue = _outcome;
    }

    function initialize(IMarket _market, uint256 _outcome) external beforeInitialized returns(bool) {
        endInitialization();
        initializeMarketValue = _market;
        initializeOutcomeValue = _outcome;
        return true;
    }

    function createShares(address _owner, uint256 _fxpValue) external onlyWhitelistedCallers returns(bool) {
        createSharesOwnerValue = _owner;
        createSharesFxpValue = _fxpValue;
        return true;
    }

    function destroyShares(address _owner, uint256 _fxpValue) external onlyWhitelistedCallers returns(bool) {
        destroySharesOwnerValue = _owner;
        destroySharesFxpValueValue = _fxpValue;
        return true;
    }

    function getTypeName() public view returns(bytes32) {
        return "ShareToken";
    }

    function getMarket() external view returns(IMarket) {
        return setMarketValue;
    }

    function getOutcome() external view returns(uint256) {
        return setOutcomeValue;
    }

    function trustedOrderTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return true;
    }

    function trustedFillOrderTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return true;
    }

    function trustedCancelOrderTransfer(address _source, address _destination, uint256 _attotokens) public onlyCaller("CancelOrder") onlyInGoodTimes afterInitialized returns (bool) {
        return true;
    }
}

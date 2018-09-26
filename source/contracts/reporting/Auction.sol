pragma solidity 0.4.24;

import 'libraries/DelegationTarget.sol';
import 'reporting/IAuction.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract Auction is DelegationTarget, Initializable, IAuction {

    IUniverse private universe;
    IReputationToken private reputationToken;
    uint256 private manualRepPriceInAttoEth = 6 * 10 ** 16;
    bool private manualModeOn = true;

    mapping(address => bool) private authorizedPriceFeeders;

    modifier onlyAuthorizedPriceFeeder {
        require(authorizedPriceFeeders[msg.sender]);
        _;
    }

    function initialize(IUniverse _universe) public beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        reputationToken = universe.getReputationToken();
        authorizedPriceFeeders[controller.owner()] = true;
        return true;
    }

    function getCurrentOfferedPrice() public view returns (uint256) {
        // TODO XXX get the current price in attoREP or attoETH of ETH / REP
        return 1;
    }

    function take(uint256 _amount) public afterInitialized returns (bool) {
        // TODO XXX purchase _amount REP / ETH at current offered price
        return true;
    }

    function getRepPriceInAttoEth() external view returns (uint256) {
        if (manualModeOn) {
            return manualRepPriceInAttoEth;
        }
        // TODO XXX return last avg price from auction
    }

    function getUniverse() public view afterInitialized returns (IUniverse) {
        return universe;
    }

    function getReputationToken() public view afterInitialized returns (IReputationToken) {
        return reputationToken;
    }

    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external afterInitialized onlyAuthorizedPriceFeeder returns (bool) {
        manualRepPriceInAttoEth = _repPriceInAttoEth;
        return true;
    }

    function addToAuthorizedPriceFeeders(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = true;
        return true;
    }

    function removeFromAuthorizedPriceFeeders(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = false;
        return true;
    }
}

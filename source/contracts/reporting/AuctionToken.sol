pragma solidity 0.4.24;

import 'reporting/IUniverse.sol';
import 'reporting/IAuctionToken.sol';
import 'Controlled.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/ITyped.sol';
import 'trading/ICash.sol';
import 'libraries/Initializable.sol';
import 'reporting/IAuction.sol';


contract AuctionToken is Controlled, ITyped, Initializable, VariableSupplyToken, IAuctionToken {

    string constant public name = "Auction Token";
    uint8 constant public decimals = 18;
    string constant public symbol = "AUC";

    IAuction public auction;
    IUniverse public universe;
    ICash public cash;
    ERC20 public redemptionToken; // The token being auctioned off and recieved at redemption
    uint256 public auctionIndex;

    function initialize(IAuction _auction, ERC20 _redemptionToken, uint256 _auctionIndex) public beforeInitialized returns(bool) {
        endInitialization();
        auction = _auction;
        universe = auction.getUniverse();
        cash = ICash(controller.lookup("Cash"));
        redemptionToken = _redemptionToken;
        auctionIndex = _auctionIndex;
        return true;
    }

    function mintForPurchaser(address _purchaser, uint256 _amount) public returns (bool) {
        require(msg.sender == address(auction));
        mint(_purchaser, _amount);
        return true;
    }

    function redeem() public returns (bool) {
        require(auction.getAuctionIndexForCurrentTime() > auctionIndex);
        uint256 _ownerBalance = balances[msg.sender];
        uint256 _tokenBalance = redemptionToken.balanceOf(this);
        uint256 _redemptionAmount = _ownerBalance.mul(_tokenBalance).div(totalSupply());
        burn(msg.sender, _ownerBalance);
        if (redemptionToken == ERC20(cash)) {
            cash.withdrawEtherTo(msg.sender, _redemptionAmount);
        } else {
            redemptionToken.transfer(msg.sender, _redemptionAmount);
        }
        return true;
    }

    function retrieveFunds() public returns (bool) {
        require(msg.sender == address(auction));
        // If no participants have claim to any funds remaining we send them back to the auction
        if (totalSupply() == 0) {
            redemptionToken.transfer(msg.sender, redemptionToken.balanceOf(this));
        }
        return true;
    }

    function getTypeName() public view returns(bytes32) {
        return "AuctionToken";
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logAuctionTokensTransferred(universe, _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        maxSupply = maxSupply.max(totalSupply());
        controller.getAugur().logAuctionTokenMinted(universe, _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logAuctionTokenBurned(universe, _target, _amount);
        return true;
    }
}

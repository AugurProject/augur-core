pragma solidity 0.4.20;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'trading/IShareToken.sol';
import 'trading/ICash.sol';


contract MaliciousMarket {
    IMarket private victimMarket;
    uint256 public getNumTicks = 1;

    function MaliciousMarket(IMarket _market) public {
        victimMarket = _market;
    }

    function getShareToken(uint256 _outcome)  public view returns (IShareToken) {
        return victimMarket.getShareToken(_outcome);
    }

    function getNumberOfOutcomes() public view returns (uint256) {
        return victimMarket.getNumberOfOutcomes();
    }

    function getDenominationToken() public view returns (ICash) {
        return victimMarket.getDenominationToken();
    }

    function getUniverse() public view returns (IUniverse) {
        return victimMarket.getUniverse();
    }
}
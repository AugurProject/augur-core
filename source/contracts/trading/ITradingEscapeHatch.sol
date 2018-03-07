pragma solidity 0.4.20;


import 'reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) public returns(bool);
}

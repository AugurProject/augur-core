pragma solidity 0.4.24;


import 'reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) public returns(bool);
}

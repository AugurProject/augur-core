pragma solidity 0.4.18;


import 'reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) public returns(bool);
}

pragma solidity ^0.4.13;

import 'reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) returns(bool);
}

pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) returns(bool);
}

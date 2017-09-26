pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';


contract ITradingEscapeHatch {
    function claimSharesInUpdate(IMarket) returns(bool);
}

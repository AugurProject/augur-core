pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Interfaces.sol';


contract BranchFactory {
    function createBranch(Controller _controller, IBranch _parentBranch, int256 _parentPayoutDistributionHash) returns (IBranch) {
        Delegator _delegator = new Delegator(_controller, "Branch");
        IBranch _branch = IBranch(_delegator);
        _branch.initialize(_parentBranch, _parentPayoutDistributionHash);
        return _branch;
    }
}

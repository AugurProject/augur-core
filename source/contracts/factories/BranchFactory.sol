pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';
import 'ROOT/reporting/IBranch.sol';


contract BranchFactory {
    function createBranch(IController _controller, IBranch _parentBranch, bytes32 _parentPayoutDistributionHash) returns (IBranch) {
        Delegator _delegator = new Delegator(_controller, "Branch");
        IBranch _branch = IBranch(_delegator);
        _branch.initialize(_parentBranch, _parentPayoutDistributionHash);
        return _branch;
    }
}

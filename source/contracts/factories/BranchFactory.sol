pragma solidity ^0.4.13;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IBranch.sol';


contract BranchFactory {
    function createBranch(IController _controller, IBranch _parentBranch, bytes32 _parentPayoutDistributionHash) returns (IBranch) {
        Delegator _delegator = new Delegator(_controller, "Branch");
        IBranch _branch = IBranch(_delegator);
        _branch.initialize(_parentBranch, _parentPayoutDistributionHash);
        return _branch;
    }
}

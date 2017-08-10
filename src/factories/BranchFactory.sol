pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/Interfaces.sol';


contract BranchFactory {
    function createBranch(Controller _controller, Branch _parentBranch, bytes32 _parentPayoutDistributionHash) returns (Branch) {
        Delegator _delegator = new Delegator(_controller, "Branch");
        Branch _branch = Branch(_delegator);
        _branch.initialize(_parentBranch, _parentPayoutDistributionHash);
        return _branch;
    }
}

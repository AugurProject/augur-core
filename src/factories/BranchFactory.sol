pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Branch {
    function initialize(address _parentBranch, int256 _parentPayoutDistributionHash);
}


contract BranchFactory {
    function createBranch(Controller _controller, Branch _parentBranch, int256 _parentPayoutDistributionHash) returns (Branch) {
        Delegator _delegator = new Delegator(_controller, "branch");
        Branch _branch = Branch(_delegator);
        _branch.initialize(_parentBranch, _parentPayoutDistributionHash);
        return _branch;
    }
}

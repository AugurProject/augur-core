pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';

// FIXME: remove once this can be imported as a solidty contract
contract Branch {
    function initialize(address parentBranch, int256 parentPayoutDistributionHash);
}

contract BranchFactory {

    function createBranch(address controller, address parentBranch, int256 parentPayoutDistributionHash) returns (Branch) {
        Delegator del = new Delegator(controller, 'branch');
        Branch branch = Branch(del);
        branch.initialize(parentBranch, parentPayoutDistributionHash);
        return branch;
    }
}

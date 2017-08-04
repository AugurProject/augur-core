pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';


// FIXME this can be removed once the contract is implemented in Solidity
contract Branch {
    function stub () {}
}


contract ReputationFaucet is Controlled {
    event FundedAccount(address indexed _branch, address indexed _sender, uint256 _repBalance, uint256 _timestamp);

    function reputationFaucet(Branch _branch) returns (bool) {
        // FIXME: no longer works with new reporting system
        // CONSIDER: we should replace this faucet with a contract added to the controller named `legacyRepContract`, then that would be the faucet and no need for sketchy code mixed in with our production code
        // REPUTATION_TOKEN.transfer(branch, msg.sender, 47*WEI_TO_ETH)
        FundedAccount(_branch, msg.sender, 47 * 10 ** 18, block.timestamp);
        return(true);
    }
}



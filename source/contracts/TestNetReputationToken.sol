pragma solidity 0.4.24;

import 'libraries/ContractExists.sol';
import 'reporting/ReputationToken.sol';


contract TestNetReputationToken is ReputationToken {
    using ContractExists for address;

    uint256 private constant DEFAULT_FAUCET_AMOUNT = 47 ether;
    address private constant FOUNDATION_REP_ADDRESS = address(0x1985365e9f78359a9B6AD760e32412f4a445E862);

    constructor() public {
        // This is to confirm we are not on foundation network
        require(!FOUNDATION_REP_ADDRESS.exists());
    }

    function faucet(uint256 _amount) public returns (bool) {
        if (_amount == 0) {
            _amount = DEFAULT_FAUCET_AMOUNT;
        }
        require(_amount < 2 ** 128);
        mint(msg.sender, _amount);
        return true;
    }
}

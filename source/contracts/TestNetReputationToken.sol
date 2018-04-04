pragma solidity 0.4.20;

import 'libraries/ContractExists.sol';
import 'reporting/ReputationToken.sol';


contract TestNetReputationToken is ReputationToken {
    using ContractExists for address;

    uint256 private constant DEFAULT_FAUCET_AMOUNT = 47 ether;
    address private constant FOUNDATION_REP_ADDRESS = address(0xE94327D07Fc17907b4DB788E5aDf2ed424adDff6);

    function TestNetReputationToken() public {
        // This is to confirm we are not on foundation network
        require(!FOUNDATION_REP_ADDRESS.exists());
    }

    function faucet(uint256 _amount) public whenNotMigratingFromLegacy returns (bool) {
        if (_amount == 0) {
            _amount = DEFAULT_FAUCET_AMOUNT;
        }
        require(_amount < 2 ** 128);
        mint(msg.sender, _amount);
        return true;
    }
}
pragma solidity 0.4.20;

import 'libraries/ContractExists.sol';
import 'libraries/Ownable.sol';
import 'libraries/token/VariableSupplyToken.sol';


contract LegacyReputationToken is VariableSupplyToken, Ownable {
    using ContractExists for address;
    event FundedAccount(address indexed _universe, address indexed _sender, uint256 _repBalance, uint256 _timestamp);
    event Pause();
    event Unpause();

    uint256 private constant DEFAULT_FAUCET_AMOUNT = 47 ether;
    address private constant FOUNDATION_REP_ADDRESS = address(0xE94327D07Fc17907b4DB788E5aDf2ed424adDff6);

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    bool public paused = false;

    /**
     * @dev modifier to allow actions only when the contract IS paused
     */
    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    /**
     * @dev modifier to allow actions only when the contract IS NOT paused
     */
    modifier whenPaused {
        require(paused);
        _;
    }

    function LegacyReputationToken() public {
        // This is to confirm we are not on foundation network
        require(!FOUNDATION_REP_ADDRESS.exists());
    }

    function faucet(uint256 _amount) public returns (bool) {
        if (_amount == 0) {
            _amount = DEFAULT_FAUCET_AMOUNT;
        }
        require(_amount < 2 ** 128);
        mint(msg.sender, _amount);
        FundedAccount(this, msg.sender, _amount, block.timestamp);
        return true;
    }

    function onMint(address, uint256) internal returns (bool) {
        return true;
    }

    function onBurn(address, uint256) internal returns (bool) {
        return true;
    }

    function onTokenTransfer(address, address, uint256) internal returns (bool) {
        return true;
    }

    /**
     * @dev called by the owner to pause, triggers stopped state
     */
    function pause() public onlyOwner whenNotPaused returns (bool) {
        paused = true;
        Pause();
        return true;
    }

    /**
     * @dev called by the owner to unpause, returns to normal state
     */
    function unpause() public onlyOwner whenPaused returns (bool) {
        paused = false;
        Unpause();
        return true;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }
}

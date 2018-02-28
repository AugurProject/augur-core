pragma solidity 0.4.20;


import 'legacy_reputation/Initializable.sol';
import 'legacy_reputation/PausableToken.sol';
import 'legacy_reputation/ERC20Basic.sol';


/**
 * @title REP2 Token
 * @dev REP2 Mintable Token with migration from legacy contract
 */
contract LegacyRepToken is Initializable, PausableToken {
    ERC20Basic public legacyReputationToken;
    uint256 public targetSupply;

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    event Migrated(address indexed holder, uint256 amount);

    /**
     * @dev Creates a new RepToken instance
     * @param _legacyReputationToken Address of the legacy ERC20Basic REP contract to migrate balances from
     */
    function LegacyRepToken(address _legacyReputationToken, uint256 _amountUsedToFreeze, address _accountToSendFrozenRepTo) {
        require(_legacyReputationToken != 0);
        legacyReputationToken = ERC20Basic(_legacyReputationToken);
        targetSupply = legacyReputationToken.totalSupply();
        balances[_accountToSendFrozenRepTo] = _amountUsedToFreeze;
        totalSupply = _amountUsedToFreeze;
        pause();
    }

    /**
     * @dev Copies the balance of a batch of addresses from the legacy contract
     * @param _holders Array of addresses to migrate balance
     * @return True if operation was completed
     */
    function migrateBalances(address[] _holders) onlyOwner beforeInitialized returns (bool) {
        for (uint256 i = 0; i < _holders.length; i++) {
            migrateBalance(_holders[i]);
        }
        return true;
    }

    /**
     * @dev Copies the balance of a single addresses from the legacy contract
     * @param _holder Address to migrate balance
     * @return True if balance was copied, false if was already copied or address had no balance
     */
    function migrateBalance(address _holder) onlyOwner beforeInitialized returns (bool) {
        if (balances[_holder] > 0) {
            return false; // Already copied, move on
        }

        uint256 amount = legacyReputationToken.balanceOf(_holder);
        if (amount == 0) {
            return false; // Has no balance in legacy contract, move on
        }

        balances[_holder] = amount;
        totalSupply = totalSupply.add(amount);
        Migrated(_holder, amount);

        if (targetSupply == totalSupply) {
            endInitialization();
        }
        return true;
    }

    /**
     * @dev Unpauses the contract with the caveat added that it can only happen after initialization.
     */
    function unpause() onlyOwner whenPaused afterInitialized returns (bool) {
        super.unpause();
        return true;
    }
}

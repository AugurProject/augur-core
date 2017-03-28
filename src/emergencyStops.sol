pragma solidity ^0.4.4;


/*
 * Ownable
 *
 * Base contract with an owner.
 * Provides onlyOwner modifier, which prevents function from running if it is called by anyone other than the owner.
 */
contract Ownable {
  address public owner;

  function Ownable() {
    owner = msg.sender;
  }

  modifier onlyOwner() {
    if (msg.sender == owner)
      _;
  }

  function transferOwnership(address newOwner) onlyOwner {
    if (newOwner != address(0)) owner = newOwner;
  }

}


/*
 * Stoppable
 * Abstract contract that allows children to implement an
 * emergency stop mechanism.
 */
 
// "Some grounds for reformation are of special interest to smart contracts. That includes mutual mistake, which covers the so-called “scrivener’s error,” an “accidental deviation from the parties’ agreement” made while recording the agreement in writing [19]. In smart contracts, the risk of this error is high because of, again, the introduction of code to contracting."

// todoupgrade contract modification / updates

contract Stoppable is Ownable {
  bool public stopped;

  modifier stopInEmergency { if (!stopped) _; }
  modifier onlyInEmergency { if (stopped) _; }

  // called by the owner on emergency, triggers stopped state
  function emergencyStop() external onlyOwner {
    stopped = true;
  }

  // called by the owner on end of emergency, returns to normal state
  function release() external onlyOwner onlyInEmergency {
    stopped = false;
  }

}
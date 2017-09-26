pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';


contract DelegationTarget is Controlled {
    bytes32 public controllerLookupName;
}

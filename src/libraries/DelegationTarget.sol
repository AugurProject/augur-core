pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';


contract DelegationTarget {
    Controller public controller;
    bytes32 public controllerLookupName;
}

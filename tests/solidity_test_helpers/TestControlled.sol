pragma solidity ^0.4.17;

import 'Controlled.sol';


contract TestControlled is Controlled {
    function deposit() public payable { }

    function setMayExtractETH(bool _mayExtractETH) public returns (bool) {
        mayExtractETH = _mayExtractETH;
    }

    function setTokenExtractionDisallowed(address _token, bool _disallowed) public returns (bool) {
        tokenExtractionDisallowed[_token] = _disallowed;
    }
}

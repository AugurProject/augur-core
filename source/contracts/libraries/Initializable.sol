pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";


contract Initializable {
    bool private initialized = false;

    modifier afterInitialized {
        require(initialized);
        _;
    }

    modifier beforeInitialized {
        require(!initialized);
        _;
    }

    function endInitialization() internal beforeInitialized returns (bool) {
        initialized = true;
        return true;
    }

    function getInitialized() constant returns (bool) {
        return initialized;
    }
}

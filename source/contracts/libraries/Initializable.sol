pragma solidity 0.4.24;



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

    function getInitialized() public view returns (bool) {
        return initialized;
    }
}

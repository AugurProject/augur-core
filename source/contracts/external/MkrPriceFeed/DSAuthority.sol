pragma solidity 0.4.20;


contract DSAuthority {
    function canCall(address src, address dst, bytes4 sig) public view returns (bool);
}


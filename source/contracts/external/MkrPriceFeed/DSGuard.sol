pragma solidity 0.4.20;

import 'external/MkrPriceFeed/DSAuth.sol';
import 'external/MkrPriceFeed/DSAuthority.sol';
import 'external/MkrPriceFeed/DSGuardEvents.sol';


contract DSGuard is DSAuth, DSAuthority, DSGuardEvents {
    bytes32 constant public ANY = bytes32(uint(-1));

    mapping (bytes32 => mapping (bytes32 => mapping (bytes32 => bool))) acl;

    function canCall(address src_, address dst_, bytes4 sig) public view returns (bool) {
        bytes32 src = bytes32(src_);
        bytes32 dst = bytes32(dst_);

        return acl[src][dst][sig]
            || acl[src][dst][ANY]
            || acl[src][ANY][sig]
            || acl[src][ANY][ANY]
            || acl[ANY][dst][sig]
            || acl[ANY][dst][ANY]
            || acl[ANY][ANY][sig]
            || acl[ANY][ANY][ANY];
    }

    function permit(bytes32 src, bytes32 dst, bytes32 sig) private auth {
        acl[src][dst][sig] = true;
        LogPermit(src, dst, sig);
    }

    function forbid(bytes32 src, bytes32 dst, bytes32 sig) public auth {
        acl[src][dst][sig] = false;
        LogForbid(src, dst, sig);
    }

    function permit(address src, address dst, bytes32 sig) public {
        permit(bytes32(src), bytes32(dst), sig);
    }

    function forbid(address src, address dst, bytes32 sig) public {
        forbid(bytes32(src), bytes32(dst), sig);
    }

}

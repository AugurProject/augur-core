from binascii import hexlify
from ethereum import utils as u
from ethereum.abi import ContractTranslator
from ethereum.config import config_metropolis, Env
from ethereum.tools import tester
from ethereum.tools.tester import ABIContract
from json import dumps as json_dumps
from os import remove as os_remove
from solc import compile_standard

config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

uint256 = """
library int256Math {
    // Signed ints with n bits can range from -2**(n-1) to (2**(n-1) - 1)
    int256 private constant INT256_MIN = -2**(255);
    int256 private constant INT256_MAX = (2**(255) - 1);

    function mul(int256 a, int256 b) internal view returns (int256) {
        int256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function div(int256 a, int256 b) internal view returns (int256) {
        int256 c = a / b;
        return c;
    }

    function sub(int256 a, int256 b) internal view returns (int256) {
        require(((a >= 0) && (b >= a - INT256_MAX)) || ((a < 0) && (b <= a - INT256_MIN)));
        return a - b;
    }

    function add(int256 a, int256 b) internal view returns (int256) {
        require(((a >= 0) && (b <= INT256_MAX - a)) || ((a < 0) && (b >= INT256_MIN - a)));
        return a + b;
    }

    function min(int256 a, int256 b) internal view returns (int256) {
        if (a <= b) {
            return a;
        } else {
            return b;
        }
    }

    function max(int256 a, int256 b) internal view returns (int256) {
        if (a >= b) {
            return a;
        } else {
            return b;
        }
    }

    function getInt256Min() internal view returns (int256) {
        return INT256_MIN;
    }

    function getInt256Max() internal view returns (int256) {
        return INT256_MAX;
    }

    // Float [fixed point] Operations
    function fxpMul(int256 a, int256 b, int256 base) internal view returns (int256) {
        return div(mul(a, b), base);
    }

    function fxpDiv(int256 a, int256 b, int256 base) internal view returns (int256) {
        return div(mul(a, base), b);
    }
}
"""

int256 = """
library uint256Math {
    function mul(uint256 a, uint256 b) internal view returns (uint256) {
        uint256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function div(uint256 a, uint256 b) internal view returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function sub(uint256 a, uint256 b) internal view returns (uint256) {
        require(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal view returns (uint256) {
        uint256 c = a + b;
        require(c >= a);
        return c;
    }

    function min(uint256 a, uint256 b) internal view returns (uint256) {
        if (a <= b) {
            return a;
        } else {
            return b;
        }
    }

    function max(uint256 a, uint256 b) internal view returns (uint256) {
        if (a >= b) {
            return a;
        } else {
            return b;
        }
    }

    // Float [fixed point] Operations
    function fxpMul(uint256 a, uint256 b, uint256 base) internal view returns (uint256) {
        return div(mul(a, b), base);
    }

    function fxpDiv(uint256 a, uint256 b, uint256 base) internal view returns (uint256) {
        return div(mul(a, base), b);
    }
}
"""

solCode = """
import 'int256.sol';
import 'uint256.sol';
contract Foo {
    using int256Math for int256;
    using uint256Math for uint256;

    function apple() returns (int256) {
        return int256(5).min(int256(-5));
    }

    function banana() returns (uint256) {
        return uint256(2**256-1).min(uint256(0));
    }
}
"""

def uploadSolidityContract(chain, compileResult, name, contractName):
    print compileResult['contracts'][name][contractName]['evm']['bytecode']['object']
    bytecode = bytearray.fromhex(compileResult['contracts'][name][contractName]['evm']['bytecode']['object'])
    signature = compileResult['contracts'][name][contractName]['abi']
    address = long(hexlify(chain.contract(bytecode, language='evm')), 16)
    contract = ABIContract(chain, ContractTranslator(signature), address)
    return contract

def compileSolidity(chain, name, code):
    result = compile_standard({
        'language': 'Solidity',
        'sources': {
            'uint256.sol': { 'content': uint256 },
            'int256.sol': { 'content': int256 },
            name: { 'content': code },
        },
        'settings': {
            'outputSelection': { '*': [ 'metadata', 'evm.bytecode', 'evm.sourceMap' ] }
        }
    })
    return result

def compileAndUpload(chain, name, code, contracts):
    compileResult = compileSolidity(chain, name, code)
    return (uploadSolidityContract(chain, compileResult, name, contractName) for contractName in contracts)

chain = tester.Chain(env=Env(config=config_metropolis))
logs = []
compileAndUpload(chain, 'uint256.sol', uint256, ['uint256Math'])
compileAndUpload(chain, 'int256.sol', int256, ['int256Math'])
foo, = compileAndUpload(chain, 'Sol', solCode, ['Foo'])
chain.head_state.log_listeners.append(lambda log: logs.append(foo.translator.listen(log)))
print foo.apple()
print foo.banana()
print logs

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

library = """
def bar():
    return(1: uint256)
"""

serCode = """
extern solExterns: [apple:[uint8]:_]
def banana(sol):
    return sol.apple(0x123456)
"""

solCode = """
contract Cash {
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => bool)) public approvals;
    function transfer(address _destination, uint256 _amount) external {
        require(balances[msg.sender] <= _amount);
        balances[msg.sender] -= _amount;
        balances[_destination] += _amount;
    }
    function transferFrom(address _source, address _destination, uint256 _amount) external {
        require(balances[_source] <= _amount);
        require(approvals[_source][msg.sender]);
        balances[_source] -= _amount;
        balances[_destination] += _amount;
    }
    function approve(address _spender, uint256 _amount) external {
        approvals[msg.sender][_spender] = true;
    }
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    function withdraw(address _target, uint256 _amount) external {
        require(_amount <= balances[_target]);
        require(approvals[_target][msg.sender]);
        balances[_target] -= _amount;
        _target.transfer(_amount);
    }
}

contract ApprovalTarget {
    Cash public cash;
    Market public market;
    function transfer(address _source, address _destination, uint256 _amount) external {
        require(Market(msg.sender) == market);
        cash.transferFrom(_source, _destination, _amount);
    }
    function withdraw(address _target, uint256 _amount) external {
        require(Market(msg.sender) == market);
        cash.withdraw(_target, _amount);
    }
    function initialize(Cash _cash, Market _market) external {
        cash = _cash;
        market = _market;
    }
}

contract Market {
    Cash public cash;
    ApprovalTarget public approvalTarget;
    modifier wrapEth() {
        if (msg.value > 0) {
            cash.deposit.value(msg.value)();
            cash.transfer(msg.sender, msg.value);
        }
        _;
    }
    modifier unwrapEth(address _target) {
        _;
        uint256 _balance = cash.balances(_target);
        if (_balance > 0) {
            approvalTarget.withdraw(_target, _balance);
        }
    }
    function apple() external wrapEth payable {
        approvalTarget.transfer(msg.sender, this, 1 ether);
    }
    function banana() external unwrapEth(msg.sender) {
        cash.transfer(msg.sender, 1 ether);
    }
    function initialize(Cash _cash, ApprovalTarget _approvalTarget) {
        cash = _cash;
        approvalTarget = _approvalTarget;
    }
}
"""

def uploadSolidityContract(chain, compileResult, name, contractName):
    bytecode = bytearray.fromhex(compileResult['contracts'][name][contractName]['evm']['bytecode']['object'])
    signature = compileResult['contracts'][name][contractName]['abi']
    address = long(hexlify(chain.contract(bytecode)), 16)
    contract = ABIContract(chain, ContractTranslator(signature), address)
    return contract

def compileSolidity(chain, name, code):
    result = compile_standard({ 'language': 'Solidity', 'sources': { name: { 'content': code } } })
    return result

def compileAndUpload(chain, name, code, contracts):
    compileResult = compileSolidity(chain, name, code)
    return (uploadSolidityContract(chain, compileResult, name, contractName) for contractName in contracts)

with open("garbage.se", "w") as file:
    file.write(library)

try:
    chain = tester.Chain(env=Env(config=config_metropolis))
    logs = []
    cash, approvalTarget, market = compileAndUpload(chain, 'Sol', solCode, ['Cash', 'ApprovalTarget', 'Market'])
    # ser = chain.contract(serCode, language="serpent")
    chain.head_state.log_listeners.append(lambda log: logs.append(cash.translator.listen(log)))
    chain.head_state.log_listeners.append(lambda log: logs.append(approvalTarget.translator.listen(log)))
    chain.head_state.log_listeners.append(lambda log: logs.append(market.translator.listen(log)))
    market.initialize(cash.address, approvalTarget.address)
    approvalTarget.initialize(cash.address, market.address)
    cash.approve(approvalTarget.address, 10**18)
    market.apple(value = 10**18)
    print 'alice eth: %s' % chain.head_state.get_balance(tester.a0)
    print 'cash eth: %s' % chain.head_state.get_balance(cash.address)
    print 'alice cash: %s' % cash.balances(tester.a0)
    print 'market cash: %s' % cash.balances(market.address)
    print '----'
    market.banana()
    print 'alice eth: %s' % chain.head_state.get_balance(tester.a0)
    print 'cash eth: %s' % chain.head_state.get_balance(cash.address)
    print 'alice cash: %s' % cash.balances(tester.a0)
    print 'market cash: %s' % cash.balances(market.address)
    print logs
finally:
    os_remove("garbage.se")

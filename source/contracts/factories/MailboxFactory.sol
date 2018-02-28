pragma solidity 0.4.20;


import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IMailbox.sol';


contract MailboxFactory {
    function createMailbox(IController _controller, address _owner) public returns (IMailbox) {
        Delegator _delegator = new Delegator(_controller, "Mailbox");
        IMailbox _mailbox = IMailbox(_delegator);
        _mailbox.initialize(_owner);
        return _mailbox;
    }
}

pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'reporting/IMailbox.sol';
import 'reporting/IMarket.sol';
import 'IControlled.sol';


contract MailboxFactory is CloneFactory {
    function createMailbox(IController _controller, address _owner, IMarket _market) public returns (IMailbox) {
        IMailbox _mailbox = IMailbox(createClone(_controller.lookup("Mailbox")));
        IControlled(_mailbox).setController(_controller);
        _mailbox.initialize(_owner, _market);
        return _mailbox;
    }
}

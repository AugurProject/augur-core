/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;


library Trading {
    enum TradeTypes {
        // FIXME: None is a placeholder to force Bid to equal 1 and Ask to equal 2, since these are their values in the Serpent files and test scripts.  After the Solidity migration is done, we should remove "None" and change Bid to 0 and Ask to 1 everywhere.
        None, Bid, Ask
    }
}

pragma solidity 0.4.24;

import "browser/StateMachine.sol";

contract Delegator {
    /////////////
    // Structs //
    /////////////
    
    address[] addressBook;
    address public owner;

    ///////////////
    // Modifiers //
    ///////////////

    //////////////
    //  Events  //
    //////////////
    
    event NewQuery(address[] clientArray, address StateMachineAddress);

    ///////////////
    // Functions //
    ///////////////
    
    constructor() public {
        owner = msg.sender;
    }
    
    function makeQuery(address[] _clientArray, bytes32[] _modelAddrs) external payable {
        StateMachine machine = (new StateMachine).value(msg.value)(msg.sender, _clientArray);
        address machineAddress = address(machine);
        addressBook.push(machineAddress);
        emit NewQuery(_clientArray, machineAddress);
        machine.newModel(_modelAddrs);
    }
}

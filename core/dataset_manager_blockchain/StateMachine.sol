pragma solidity 0.4.24;


contract StateMachine {
    

    /////////////
    // Structs //
    /////////////
    
    address validator;
    address[] listeners;
    bytes32[] modelAddrs;
    uint balance;
    enum Stages {
        Training,
        Validating
    }

    // This is the current stage.
    Stages public stage = Stages.Validating;

    ///////////////
    // Modifiers //
    ///////////////
    modifier onlyBy(address _account)
    {
        require(
            msg.sender == _account,
            "Sender not authorized."
        );
        _;
    }
    modifier atStage(Stages _stage) {
        require(
            stage == _stage,
            "Function cannot be called at this time."
        );
        _;
    }
    //////////////
    //  Events  //
    //////////////

    event NewModel();
    event DoneTraining();

    ///////////////
    // Functions //
    ///////////////

    constructor (address _validator, address[] _listeners) public payable {
        validator = _validator;
        listeners = _listeners;
    }
    
    function newModel(bytes32[] _newModelAddrs) 
        external onlyBy(validator) atStage(Stages.Validating) {
        modelAddrs = _newModelAddrs;
        emit NewModel();
        nextStage();
    }
    
    function viewValidator() 
        view external returns (address) {
        return validator;
    }
    
    function nextStage() internal {
        stage = Stages(uint(stage) + 1);
    }
    
    function reward(uint _amt) 
        external onlyBy(validator) atStage(Stages.Training) {
        uint len = listeners.length;
        for (uint i = 0; i < len; i ++) {
            listeners[i].transfer(_amt);
        }
        nextStage();
    }
    
    function terminate()
        external onlyBy(validator) atStage(Stages.Validating) {
            emit DoneTraining();
            selfdestruct(validator);
        }
}
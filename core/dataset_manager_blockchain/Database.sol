pragma solidity 0.4.24;


contract Database {
    
    /////////////
    // Structs //
    /////////////
    
    struct dbEntry {
        string value;
    }
    
    ///////////////
    // Modifiers //
    ///////////////

    //////////////
    //  Events  //
    //////////////
    
    //this is the key-value store
    mapping(bytes32 => dbEntry) public metaDb;
    
    ///////////////
    // Functions //
    ///////////////
    
    constructor() public {
        //this is the constructor
    }

    //this is the setter method for the key-value store
    function setter(bytes32 key, string value) public {
        metaDb[key] = dbEntry(value);
    }

    //this is the getter method for the key-value store
    function getter(bytes32 key) public view returns (string) {
        dbEntry memory x = metaDb[key];
        return (x.value);
    }

}

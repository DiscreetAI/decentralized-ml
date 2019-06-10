exports.bootstrap = require('./data_manager.js').DataManager.bootstrap;
exports.store = require('./data_manager.js').DataManager.store;

exports.printMsg = function() {
    console.log("This is a message from the demo package");
}

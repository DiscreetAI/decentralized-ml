exports.bootstrap = require('./data_manager.js').DataManager.bootstrap;
exports.store = require('./data_manager.js').DataManager.store;
exports.listen = require('./data_manager').DataManager._listen;
exports.is_bootstrapped = require('./data_manager').DataManager.bootstrapped;
exports.has_data = require('./data_manager').DataManager.has_data;

exports.printMsg = function() {
    console.log("This is a message from the demo package");
}

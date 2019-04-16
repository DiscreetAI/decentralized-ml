"use strict";
exports.__esModule = true;
var DMLDB = /** @class */ (function () {
    function DMLDB() {
    }
    DMLDB.prototype.open = function (callback) {
        // Database version.
        var version = 1;
        // Open a connection to the datastore.
        var request = indexedDB.open('data_mappings', version);
        // Handle datastore upgrades.
        request.onupgradeneeded = function (e) {
            var db = e.target.result;
            //e.target.transaction.onerror = tDB.onerror;
            // Delete the old datastore.
            if (db.objectStoreNames.contains('dataMapping')) {
                db.deleteObjectStore('dataMapping');
            }
            // Create a new datastore.
            var store = db.createObjectStore('dataMapping', {
                keyPath: 'repo'
            });
        };
        // Handle successful datastore access.
        request.onsuccess = function (e) {
            // Get a reference to the DB.
            DMLDB.datastore = e.target.result;
            // Execute the callback.
            callback();
        };
        // Handle errors when opening the datastore.
        //request.onerror = this.onerror;
    };
    ;
    DMLDB.prototype.create = function (repo, data, callback) {
        // Get a reference to the db.
        var db = DMLDB.datastore;
        // Initiate a new transaction.
        var transaction = db.transaction(['dataMapping'], 'readwrite');
        // Get the datastore.
        var objStore = transaction.objectStore('dataMapping');
        // Create a timestamp for the dataMapping item.
        var timestamp = new Date().getTime();
        // Create an object for the dataMapping item.
        var dataMapping = {
            'data': data,
            'repo': repo,
            'timestamp': timestamp
        };
        // Create the datastore request.
        var request = objStore.put(dataMapping);
        // Handle a successful datastore put.
        request.onsuccess = function (e) {
            // Execute the callback function.
            callback(dataMapping);
        };
        // Handle errors.
        //request.onerror = tDB.onerror;
    };
    ;
    DMLDB.prototype.get = function (dml_request, callback) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['dataMapping'], 'readwrite');
        var objStore = transaction.objectStore('dataMapping');
        var request = objStore.get(dml_request.repo);
        request.onsuccess = function (e) {
            callback(request.result, dml_request);
        };
        request.onerror = function (e) {
            console.log(e);
        };
    };
    ;
    DMLDB.prototype["delete"] = function (repo, callback) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['dataMapping'], 'readwrite');
        var objStore = transaction.objectStore('dataMapping');
        var request = objStore["delete"](repo);
        request.onsuccess = function (e) {
            callback();
        };
        request.onerror = function (e) {
            console.log(e);
        };
    };
    ;
    return DMLDB;
}());
exports.DMLDB = DMLDB;

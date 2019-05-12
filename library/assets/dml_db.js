"use strict";
export var DMLDB = /** @class */ (function () {
    function DMLDB() {
    }
    DMLDB.open = function (callback) {
        // Database version.
        var version = 1;
        // Open a connection to the datastore.
        var request = indexedDB.open('datamappings', version);
        // Handle datastore upgrades.
        request.onupgradeneeded = function (e) {
            var db = e.target.result;
            //e.target.transaction.onerror = tDB.onerror;
            // Delete the old datastore.
            if (db.objectStoreNames.contains('datamapping')) {
                db.deleteObjectStore('datamapping');
            }
            // Create a new datastore.
            var store = db.createObjectStore('datamapping', {
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
    DMLDB.create = function (repo, data, callback, ws, node) {
        console.log("Start");
        // Get a reference to the db.
        var db = DMLDB.datastore;
        // Initiate a new transaction.
        var transaction = db.transaction(['datamapping'], 'readwrite');
        // Get the datastore.
        var objStore = transaction.objectStore('datamapping');
        // Create a timestamp for the datamapping item.
        var timestamp = new Date().getTime();
        // Create an object for the datamapping item.
        var datamapping = {
            'data': data,
            'rows': data.length,
            'cols': data[0].length,
            'repo': repo,
            'timestamp': timestamp
        };
        // Create the datastore request.
        var request = objStore.put(datamapping);
        console.log(request);
        // Handle a successful datastore put.
        request.onsuccess = function (e) {
            // Execute the callback function.
            console.log("SUCCESS CREATE");
            callback(ws, node);
        };
        // Handle errors.
        //request.onerror = tDB.onerror;
    };
    ;
    DMLDB.get = function (dml_request, callback, model, ws) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['datamapping'], 'readwrite');
        var objStore = transaction.objectStore('datamapping');
        var request = objStore.get(dml_request.repo);
        request.onsuccess = function (e) {
            var data = tf.tensor(request.result.data).as2D(request.result.rows, request.result.cols);
            console.log("GET SUCCESS");
            callback(data, dml_request, model, ws);
        };
        request.onerror = function (e) {
            console.log(e);
        };
    };
    ;
    DMLDB.prototype["delete"] = function (repo, callback) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['datamapping'], 'readwrite');
        var objStore = transaction.objectStore('datamapping');
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

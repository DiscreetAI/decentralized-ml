"use strict";
export var DMLDB = /** @class */ (function () {
    function DMLDB() {
    }
    DMLDB._open = function () {
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
            console.log("DMLDB successfully opened!");
        };
        // Handle errors when opening the datastore.
        //request.onerror = this.onerror;
    };
    ;
    DMLDB._create = function (repo, data, callback) {
        // Get a reference to the db.
        var db = DMLDB.datastore;
        // Initiate a new transaction.
        var transaction = db.transaction(['datamapping'], 'readwrite');
        // Get the datastore.
        var objStore = transaction.objectStore('datamapping');
        // Create a timestamp for the data item.
        var timestamp = new Date().getTime();
        // Create an object for the data item.
        var datamapping = {
            'data': data,
            'rows': data.length,
            'cols': data[0].length,
            'repo': repo,
            'timestamp': timestamp,
            'sessions': {}
        };
        // Create the datastore request.
        var request = objStore.put(datamapping);
        // Handle a successful datastore put.
        request.onsuccess = function (e) {
            // Execute the callback function.
            callback();
        };
        // Handle errors.
        //request.onerror = tDB.onerror;
    };
    ;
    DMLDB._create_session = function (data, dml_request, callback, model, datamapping) {
        // Get a reference to the db.
        var db = DMLDB.datastore;
        // Initiate a new transaction.
        var transaction = db.transaction(['datamapping'], 'readwrite');
        // Get the datastore.
        var objStore = transaction.objectStore('datamapping');
        // Create an object for the data item.
        var session = {
            'round': 0
        };
        datamapping.sessions[dml_request.id] = session;
        // Create the datastore request.
        var request = objStore.put(datamapping);
        // Handle a successful datastore put.
        request.onsuccess = function (e) {
            // Execute the callback function.
            callback(data, dml_request, model);
        };
        // Handle errors.
        //request.onerror = tDB.onerror;
    };
    ;
    DMLDB._get = function (dml_request, callback, model) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['datamapping'], 'readwrite');
        var objStore = transaction.objectStore('datamapping');
        var request = objStore.get(dml_request.repo);
        request.onsuccess = function (e) {
            var data = tf.tensor(request.result.data).as2D(request.result.rows, request.result.cols);
            if (dml_request.action == 'TRAIN') {
                var sessions = request.result.sessions;
                if (!(dml_request.id in sessions)) {
                    DMLDB._create_session(data, dml_request, callback, model, request.result);
                    return;
                }
                var session_entry = sessions[dml_request.id];
                if (session_entry.round + 1 != dml_request.round) {
                    console.log("Ignoring server's message...");
                    console.log("Request's round was " + dml_request.round + " and current round is " + session_entry.round);
                    return;
                }
            }
            callback(data, dml_request, model);
        };
        request.onerror = function (e) {
            console.log(e);
        };
    };
    ;
    DMLDB._put = function (dml_request, callback, result) {
        var db = DMLDB.datastore;
        var transaction = db.transaction(['datamapping'], 'readwrite');
        var objStore = transaction.objectStore('datamapping');
        var request = objStore.get(dml_request.repo);
        request.onsuccess = function (e) {
            request.result.sessions[dml_request.id].round = dml_request.round;
            callback(dml_request, result);
        };
        request.onerror = function (e) {
            console.log(e);
        };
    };
    ;
    return DMLDB;
}());

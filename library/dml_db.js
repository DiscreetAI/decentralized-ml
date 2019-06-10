"use strict";
exports.__esModule = true;
var tfjs_1 = require("@tensorflow/tfjs-node");
var PouchDB = require('pouchdb');

var DMLDB = /** @class */ (function () {
    function DMLDB() {
    }
    DMLDB._open = function () {
        // Database version.
        var version = 1;
        // Open a connection to the datastore.
        DMLDB.db = new PouchDB('DMLDB');
    };
    ;
    DMLDB._create = function (repo, data, callback) {
        // Get a reference to the db.
        
        var timestamp = new Date().getTime();
        // Create an object for the data item.
        DMLDB.db.put({
            _id: repo,
            data: data,
            rows: data.length,
            cols: data[0].length,
            timestamp: timestamp,
            sessions: {}
        }, function(err, response) {
            if (err) { return console.log(err); }
            callback()
            // handle response
          });
        // Handle errors.
        //request.onerror = tDB.onerror;
    };
    ;
    
    DMLDB._get = function (dml_request, callback, model) {
        DMLDB.db.get(dml_request.repo, function(err, doc) {
            if (err) { return console.log(err); }
            var data = tfjs_1.tensor(doc.data).as2D(doc.rows, doc.cols);
            if (dml_request.action == 'TRAIN') {
                var sessions = doc.sessions;
                if (!(dml_request.id in sessions)) {
                    sessions[dml_request.id] = 0;
                    DMLDB.db.put({
                        _id: dml_request.repo,
                        _rev: doc._rev,
                        data: doc.data,
                        rows: doc.data.length,
                        cols: doc.data[0].length,
                        timestamp: doc.timestamp,
                        sessions: sessions
                    }, function(err, response) {
                    if (err) { return console.log(err); }
                    callback(data, dml_request, model);
                    return;
                    });
                }
                var session_entry = sessions[dml_request.id];
                if (session_entry.round + 1 != dml_request.round) {
                    console.log("Ignoring server's message...");
                    console.log("Request's round was " + dml_request.round + " and current round is " + session_entry.round);
                    return;
                }
            }
            callback(data, dml_request, model);
        });
    };
    ;

    DMLDB._put = function (dml_request, callback, result) {
        DMLDB.db.get(dml_request.repo, function(err, doc) {
            if (err) { return console.log(err); }
            doc.sessions[dml_request.id] = dml_request.round
            DMLDB.db.put({
                _id: dml_request.repo,
                _rev: doc._rev,
                data: doc.data,
                rows: doc.data.length,
                cols: doc.data[0].length,
                timestamp: doc.timestamp,
                sessions: doc.sessions
            }, function(err, response) {
                if (err) { return console.log(err); }
                callback(data, dml_request, model);
                return;
            });
        });
    };
    ;
    return DMLDB;
}());
exports.DMLDB = DMLDB;

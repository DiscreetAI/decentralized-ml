"use strict";
import { DMLDB } from './dml_db.js';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';
export var DataManager = /** @class */ (function () {
    function DataManager() {
    }
    DataManager.store = function (repo, data, ws, node) {
        DMLDB.create(repo, data.arraySync(), DataManager.listen, ws, node);
    };
    DataManager.listen = function (ws, node, db) {
        ws.addEventListener('message', function (event) {
            console.log("Received message:")
            var receivedMessage = event.data;
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request = DMLRequest.deserialize(receivedMessage);
                Runner.handleMessage(request, node, ws);
            } 
        });
    };
    return DataManager;
}());

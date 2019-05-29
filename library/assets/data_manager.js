"use strict";
import { DMLDB } from './dml_db.js';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';
export var DataManager = /** @class */ (function () {
    function DataManager() {
    }
    DataManager.store = function (repo, data, ws, node) {
        DMLDB._create(repo, data.arraySync(), DataManager._listen, ws, node);
    };
    DataManager._listen = function (ws, node, db) {
        ws.addEventListener('message', function (event) {
            console.log("Received message:")
            var receivedMessage = event.data;
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request = DMLRequest._deserialize(receivedMessage);
                Runner._handleMessage(request, node, ws);
            } 
        });
    };
    return DataManager;
}());

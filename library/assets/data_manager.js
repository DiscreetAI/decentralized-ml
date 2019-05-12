"use strict";
import {DMLDB} from "./dml_db.js";
import {DMLRequest} from "./message.js";
import {Runner} from "./runner.js";
export var DataManager = /** @class */ (function () {
    function DataManager() {
    }
    DataManager.store = function (repo, data, ws, node) {
        DMLDB.create(repo, data.arraySync(), DataManager.listen, ws, node);
    };
    DataManager.listen = function (ws, node) {
        ws.addEventListener('message', function (event) {
            var receivedMessage = event.data;
            console.log("Received message: " + receivedMessage);
            var request = DMLRequest.deserialize(receivedMessage);
            Runner.handleMessage(request, node, ws);
        });
    };
    return DataManager;
}());

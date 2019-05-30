"use strict";
import { DMLDB } from './dml_db.js';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';

export var DataManager = /** @class */ (function () {
    function DataManager() {
    }
    DataManager.bootstrap = function (repo_id) {
        DataManager.repo_id = repo_id;
        DataManager.cloud_url = "http://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com";
        DataManager.ws = new WebSocket("ws://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com");
        DataManager.ws.addEventListener("open", function (event) {
            var registrationMessage = {
                "type": "REGISTER",
                "node_type": "LIBRARY"
            };
            DataManager.ws.send(JSON.stringify(registrationMessage));
        });
        DMLDB._open();
        DataManager.bootstrapped = true;
    };
    DataManager.store = function (repo_name, data) {
        if (!DataManager.bootstrapped)
            throw new Error("Library not bootstrapped!");
        DMLDB._create(repo_name, data.arraySync(), DataManager._listen);
    };
    DataManager._listen = function () {
        DataManager.ws.addEventListener('message', function (event) {
            var receivedMessage = event.data;
            console.log("Received message:");
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request = DMLRequest._deserialize(receivedMessage);
                Runner._handleMessage(request);
            }
        });
    };
    DataManager.bootstrapped = false;
    return DataManager;
}());
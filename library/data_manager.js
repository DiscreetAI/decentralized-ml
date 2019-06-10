"use strict";
exports.__esModule = true;
var dml_db_js_1 = require("./dml_db.js");
var message_js_1 = require("./message.js");
var runner_js_1 = require("./runner.js");
const WebSocket = require('ws');

var DataManager = /** @class */ (function () {
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
        dml_db_js_1.DMLDB._open();
        DataManager.bootstrapped = true;
    };
    DataManager.store = function (repo_name, data) {
        if (!DataManager.bootstrapped)
            throw new Error("Library not bootstrapped!");
        dml_db_js_1.DMLDB._create(repo_name, data.arraySync(), DataManager._listen);
    };
    DataManager._listen = function () {
        DataManager.ws.addEventListener('message', function (event) {
            var receivedMessage = event.data;
            console.log("Received message:");
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request = message_js_1.DMLRequest._deserialize(receivedMessage);
                runner_js_1.Runner._handleMessage(request);
            }
        });
    };
    DataManager.bootstrapped = false;
    return DataManager;
}());
exports.DataManager = DataManager;

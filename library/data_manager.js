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
            console.log("opening...")
            var registrationMessage = {
                "type": "REGISTER",
                "node_type": "LIBRARY"
            };
            DataManager.ws.send(JSON.stringify(registrationMessage));
        });
        if (DataManager.bootstrapped) {
            DataManager._listen();
        } else {
            dml_db_js_1.DMLDB._open();
            DataManager.bootstrapped = true;
        }
    };
    DataManager.store = function (repo, data) {
        if (!DataManager.bootstrapped)
            throw new Error("Library not bootstrapped!");
        if (DataManager.has_data) {
            dml_db_js_1.DMLDB.update_store(repo, data, null);
        } else {
            dml_db_js_1.DMLDB._create(repo, data.arraySync(), DataManager._listen);
            DataManager.has_data = true;
        }
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

        DataManager.ws.addEventListener("close", function (event) {
            console.log("closing...")
            console.log(event);
            if (event.code == 1006) {
                DataManager.bootstrap(DataManager.repo_id);
            }
        });
    };
    DataManager.bootstrapped = false;
    DataManager.has_data = false;
    return DataManager;
}());
exports.DataManager = DataManager;

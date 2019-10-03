"use strict";
exports.__esModule = true;
var DMLDB = require("./dml_db.js").DMLDB;
var DMLRequest = require("./message.js").DMLRequest;
var runner_js_1 = require("./runner.js");
const WebSocket = require('ws');

class DataManager {
    constructor() {
        DataManager.bootstrapped = false;
        DataManager.has_data = false;
    }

    static _connect(repo_id, data, callback) {
        DataManager.repo_id = repo_id;
        DataManager.cloud_url = "http://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com";
        DataManager.ws = new WebSocket("ws://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com");
        DataManager.ws.addEventListener("open", function (event) {
            console.log("Connection successful!");
            DataManager.bootstrapped = true;
            var registrationMessage = {
                "type": "REGISTER",
                "node_type": "LIBRARY"
            };
            DataManager.ws.send(JSON.stringify(registrationMessage));
            console.log("Bootstrapped!")
            callback(repo_id, data);
        });

        DataManager.ws.addEventListener("error", function (event) {
            throw new Error("Bootstrap failed due to a failure to connect. Please check the repo id to make sure it is valid!");
            
            //console.log(event);
        });

    }

    static bootstrap(repo_id, data, callback) {
        if (DataManager.bootstrapped) {
            DataManager._listen();
        } else {
            DMLDB._open();
            DataManager._connect(repo_id, data, callback);
        }
    }

    static store(repo, data) {
        if (!DataManager.bootstrapped)
            throw new Error("Library not bootstrapped!");
        if (DataManager.has_data) {
            DMLDB.update_store(repo, data, null);
        } else {
            DMLDB._create(repo, data.arraySync(), DataManager._listen);
            DataManager.has_data = true;
        }
        console.log("Data stored!");
    }

    static bootstrap_and_store(repo_id, data) {
        DataManager.bootstrap(repo_id, data, DataManager.store);
    }

    static _listen() {
        DataManager.ws.addEventListener('message', function (event) {
            var receivedMessage = event.data;
            console.log("Received message:");
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request = DMLRequest._deserialize(receivedMessage);
                runner_js_1.Runner._handleMessage(request);
            }
        });

        DataManager.ws.addEventListener("close", function (event) {
            console.log("Connection lost. Reconnecting...")
            console.log(event);
            if (event.code == 1006) {
                DataManager.bootstrap(DataManager.repo_id);
            }
        });
    }
}
exports.DataManager = DataManager;

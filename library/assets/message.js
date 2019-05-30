"use strict";

import { DataManager } from './data_manager.js';
export var DMLRequest = /** @class */ (function () {
    function DMLRequest(id, repo, action, params) {
        this.id = id;
        this.repo = repo;
        this.action = action;
        this.params = params;
        this.round = -1;
    }
    DMLRequest._serialize = function (request, message) {
        var socketMessage = {
            "session_id": request.id,
            "action": request.action,
            "results": message,
            "type": "NEW_WEIGHTS"
        };
        if (request.action == "TRAIN")
            socketMessage["round"] = request.round;
        return JSON.stringify(socketMessage);
    };
    /* TODO: This feels more complicated than necessary */
    DMLRequest._deserialize = function (message) {
        var request_json = JSON.parse(message);
        var request = new DMLRequest(request_json["session_id"], request_json["repo_id"], request_json["action"], request_json["hyperparams"]);
        if (request.action == "TRAIN")
            request.round = request_json["round"];
        return request;
    };
    return DMLRequest;
}());

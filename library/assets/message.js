"use strict";
export var DMLRequest = /** @class */ (function () {
    function DMLRequest(id, repo, action, params, label_index) {
        this.id = id;
        this.repo = repo;
        this.action = action;
        this.params = params;
        this.label_index = label_index;
        this.round = -1;
    }
    DMLRequest.serialize = function (request, message) {
        var socketMessage = {
            "id": request.id,
            "repo": request.repo,
            "action": request.action,
            "message": message
        };
        if (request.action == "train")
            socketMessage["round"] = request.round;
        return JSON.stringify(socketMessage);
    };
    /* TODO: This feels more complicated than necessary */
    DMLRequest.deserialize = function (message) {
        var request_json = JSON.parse(message);
        var request = new DMLRequest(request_json["id"], request_json["repo"], request_json["action"], request_json["params"], request_json["label_index"]);
        if (request.action == "train")
            request.round = request_json["round"];
        return request;
    };
    return DMLRequest;
}());

import { DMLDB } from './dml_db.js';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';
import { Tensor2D } from '@tensorflow/tfjs';

declare function require(name:string):any;

export class DataManager {

    static repo_id:string;
    static ws:WebSocket;
    static cloud_url:string;
    static bootstrapped:boolean = false;

    static bootstrap (repo_id:string) {
        DataManager.repo_id = repo_id;
        DataManager.cloud_url = "http://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com";
        DataManager.ws = new WebSocket("ws://" + repo_id + ".au4c4pd2ch.us-west-1.elasticbeanstalk.com");
        DataManager.ws.addEventListener("open", function (event) {
            var registrationMessage = {
              "type": "REGISTER",
              "node_type": "LIBRARY"
            }
            DataManager.ws.send(JSON.stringify(registrationMessage));
        });
        DMLDB._open();
        DataManager.bootstrapped = true;
    }
    static store (repo_name:string, data:Tensor2D) {
        if (!DataManager.bootstrapped)
            throw new Error("Library not bootstrapped!");
        DMLDB._create(repo_name, data.arraySync(), DataManager._listen);
    }

    static _listen () {
        DataManager.ws.addEventListener('message', function (event) {
            var receivedMessage:string = event.data;
            console.log("Received message:");
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request:DMLRequest = DMLRequest._deserialize(receivedMessage);
                Runner._handleMessage(request);
            } 
        });
    }
}
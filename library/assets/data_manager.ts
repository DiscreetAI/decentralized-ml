import { DMLDB } from './dml_db.js';
import { Tensor2D } from '@tensorflow/tfjs';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';

declare function require(name:string):any;

class DataManager {

    static store (repo:string, data:Tensor2D, ws:WebSocket, node:string) {
        DMLDB._create(repo, data.arraySync(), DataManager._listen, ws, node);
    }

    static _listen (ws:WebSocket, node:string, db:DMLDB) {
        ws.addEventListener('message', function (event) {
            var receivedMessage:string = event.data;
            console.log("Received message:");
            console.log(receivedMessage);
            if ("action" in JSON.parse(receivedMessage)) {
                var request:DMLRequest = DMLRequest._deserialize(receivedMessage);
                Runner._handleMessage(request, node, ws);
            } 
        });
    }
}
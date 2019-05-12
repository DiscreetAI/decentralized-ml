import { DMLDB } from './dml_db.js';
import { Tensor2D } from '@tensorflow/tfjs';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';

declare function require(name:string):any;

class DataManager {

    static store (repo:string, data:Tensor2D, ws:WebSocket, node:string) {
        DMLDB.create(repo, data.arraySync(), DataManager.listen, ws, node);
    }

    static listen (ws:WebSocket, node:string) {
        ws.addEventListener('message', function (event) {
            var receivedMessage:string = event.data;
            var request:DMLRequest = DMLRequest.deserialize(receivedMessage);
            Runner.handleMessage(request, node, ws);
        });
    }
}
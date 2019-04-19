import { DMLDB } from './dml_db.js';
import { Tensor2D } from '@tensorflow/tfjs';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';

class DataManager {
    static store (repo:number, data:Tensor2D, node:string, db:DMLDB) {
        db.create(repo, data);
        var webSocket:WebSocket = new WebSocket(node);
        webSocket.addEventListener('message', function (event) {
            var receivedMessage:string = event.data;
            var request:DMLRequest = DMLRequest.deserialize(receivedMessage);
            Runner.handleMessage(request, db, node)
        });
    }
}
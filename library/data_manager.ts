import { DMLDB } from './dml_db.js';
import { Tensor2D } from '@tensorflow/tfjs';
import { DMLRequest } from './message.js';
import { Runner } from './runner.js';

class DataManager {
    static store (repo:number, data:Tensor2D, node:string, db:DMLDB) {
        db.create(repo, data, DataManager._listen, node, db);
    }

    static _listen (node:string, db:DMLDB) {
        // Create WebSocket connection.
        const socket = new WebSocket(node);

        // Listen for messages
        socket.addEventListener('message', function (event) {
            var receivedMessage:string = event.data;
            var request:DMLRequest = DMLRequest.deserialize(receivedMessage);
            Runner.handleMessage(request, db, node)
        });
    }
}
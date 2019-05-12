// "use strict";
// //exports.__esModule = true;
// //var dml_db_js_1 = require("./dml_db.js");
// //import { DMLDB } from "./dml_db.js";
// import { DMLRequest } from "./message.js";
// import { Runner } from "./runner.js"
// import {MnistData} from './assets/data.js';
//var tfjs_1 = require("@tensorflow/tfjs");
//import { loadLayersModel, tensor} from '@tensorflow/tfjs';

//var db = new DMLDB();

var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('Hello World!');
}).listen(8002);

var WebSocket = require("ws");
ws = new WebSocket('ws://localhost:8001');

//while(ws.readyState == ws.CONNECTING);
console.log("Client 2 successfully created WebSocket");

ws.onopen = function() {       
    // Web Socket is connected, send data using send()
    ws.send("Hi, this is Client 2!");
    //alert("Message is sent...");
    };
ws.addEventListener('message', function (event) {
    console.log(event.data);
});

async function run() {
    //db.open(after_open);
    // var dict = {
    //     "id": "id",
    //     "repo": "test",
    //     "action": "train",
    //     "round": 1,
    //     "params": {"ah": 4},
    //     "label_index": 1
    // }
    // var request = DMLRequest.deserialize(JSON.stringify(dict));
    const SOCKET_URL = "ws://localhost:8001/";

    // Runner.sendMessage(request, "Hey Server", SOCKET_URL);
    
}



// "use strict";
// //exports.__esModule = true;
// //var dml_db_js_1 = require("./dml_db.js");
var DMLDB = require("./dml_db.js");
DMLDB = DMLDB.DMLDB;
console.log(DMLDB);
// import { DMLRequest } from "./message.js";
// import { Runner } from "./runner.js"
//import { loadLayersModel, tensor} from '@tensorflow/tfjs';
var DMLRequest = require('./message.js');
DMLRequest = DMLRequest.DMLRequest;

var Runner = require("./runner.js");
Runner = Runner.Runner;

//var db = new DMLDB();

var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('Hello World!');
}).listen(8000);

var SOCKET_URL = 'ws://localhost:8001';
var node = 'http://localhost:8999'
const BATCH_SIZE = 128;

var WebSocket = require("ws");
ws = new WebSocket(SOCKET_URL);

//while(ws.readyState == ws.CONNECTING);
console.log("Client 1 successfully created WebSocket");

ws.onopen = function() {       
    // Web Socket is connected, send data using send()
    ws.send("Hi, this is Client 1!");
    //alert("Message is sent...");
    };
ws.addEventListener('message', function (event) {
    console.log("The server said: " + event.data);
});

// async function run() {
//     //db.open(after_open);
//     // var dict = {
//     //     "id": "id",
//     //     "repo": "test",
//     //     "action": "train",
//     //     "round": 1,
//     //     "params": {"ah": 4},
//     //     "label_index": 1
//     // }
//     // var request = DMLRequest.deserialize(JSON.stringify(dict));
//     const SOCKET_URL = "ws://localhost:8001/";

//     // Runner.sendMessage(request, "Hey Server", SOCKET_URL);
    
// }

function run() {
  DMLDB.open(after_open);
}

console.log("HELLO");
run();

async function after_open() {
    // var data = tf.tensor([[1, 2], [3, 4]]).as2D(2, 2);
    // console.log(data.arraySync());
    // db.create("test", data.arraySync(), after_create, "localhost");
    const data = await getData();
    console.log("Data retrieved!")
    db.create("mnist", data, DataManager.listen, ws, node, db);
    console.log("Data stored!")
    setTimeout(dml, 5000);
}

function dml() {
  var params = {
    "batch_size": BATCH_SIZE,
    "epochs": 5,
    "shuffle": true
  }
  var message = {
      "id": "test",
      "repo": "mnist",
      "action": "train",
      "params": params,
      "label_index": 0
  }
  var request = DMLRequest.deserialize(JSON.stringify(message));
  global.fetch = require('node-fetch');
  Runner.handleMessage(request, model, ws);
  //console.log(data);
  console.log("Success?");
}

function after_create(node) {
    console.log(node);
    var dict = {
        "id": "id",
        "repo": "test",
        "action": "train",
        "round": 1,
        "params": {"ah": 4},
        "label_index": 1
    }
    var request = DMLRequest.deserialize(JSON.stringify(dict));
    console.log(request);
    db.get(request, after_get, null, node);
}

function after_get(array_data, request, model, node) {
    console.log(array_data.print());
}

async function getData() {
    const fs = require('fs'); 
    const csv = require('csv-parser');
    const inputFilePath = "./assets/data.csv";

    var mnist = [];
    var output = [];
    for (var i = 0; i < 785; i++) {
        output.push([]);
    }
    

    var data = fs.readFileSync('./assets/data.csv')
        .toString() // convert Buffer to string
        .split('\n') // split string to lines
        .map(e => e.trim()) // remove white spaces for each line
        .map(e => e.split(',').map(e => e.trim())); // split each line to array

    return data;
  }
  
  async function getModel(id) {
    console.log(id);
    var model = await Runner.getModel(node, id);
    return model;
  }
  
  function getOptimizationData() {
    // TODO: Check that the optimizer is valid.
    return {
      'optimizer_config': {
        'class_name': 'SGD',
        'config': {
          'lr': 0.0010000000474974513,
          'momentum': 0.0,
          'decay': 0.0,
          'nesterov': false
        }
      },
     'loss': 'sparse_categorical_crossentropy',
     'metrics': ['accuracy'],
     'sample_weight_mode': null,
     'loss_weights': null
   }
  }
  
  function compileModel(model, optimization_data) {
  
    let optimizer;
    if (optimization_data['optimizer_config']['class_name'] == 'SGD') {
      // SGD
      optimizer = tf.train.sgd(optimization_data['optimizer_config']['config']['lr']);
    } else {
      // Not supported!
      throw "Optimizer not supported!"
    }
  
    model.compile({
      optimizer: optimizer,
      loss: _lowerCaseToCamelCase(optimization_data['loss']),
      metrics: optimization_data['metrics'],
    });
  
    console.log("Model compiled!", model);
    return model;
  }
  
  async function getValidationAccuracy(model, data) {
    const [labels, preds] = await _evaluateModel(model, data);
    const accuracy = await tf.equal(preds, labels).sum().dataSync()[0] / tf.equal(preds, labels).size;
    console.log("Accuracy calculated! ", accuracy)
    return accuracy;
  }
  
  async function retrainModel(model, data) {
    const metrics = ['loss', 'acc'];
  
    const BATCH_SIZE = 128;
    const TRAIN_DATA_SIZE = 8000;
    //const TEST_DATA_SIZE = 1000;
  
    const [trainXs, trainYs] = tf.tidy(() => {
      const d = data.nextTrainBatch(TRAIN_DATA_SIZE);
      return [
        d.xs.reshape([TRAIN_DATA_SIZE, 784]),
        d.labels.argMax([-1])
      ];
    });
  
    // const [testXs, testYs] = tf.tidy(() => {
    //   const d = data.nextTestBatch(TEST_DATA_SIZE);
    //   return [
    //     d.xs.reshape([TEST_DATA_SIZE, 784]),
    //     d.labels.argMax([-1])
    //   ];
    // });
  
    return model.fit(trainXs, trainYs, {
      batchSize: BATCH_SIZE,
      // validationData: [testXs, testYs],
      epochs: 5,
      shuffle: true,
    });
  }
  
  async function _evaluateModel(model, data) {
    const IMAGE_WIDTH = 28;
    const IMAGE_HEIGHT = 28;
    const TEST_DATA_SIZE = data.testIndices.length;
    //const TEST_DATA_SIZE = 100;
    const testData = data.nextTestBatch(TEST_DATA_SIZE);
    const testxs = testData.xs.reshape([TEST_DATA_SIZE, IMAGE_WIDTH * IMAGE_HEIGHT]);
    const labels = testData.labels.argMax([-1]);
    const preds = model.predict(testxs).argMax([-1]);
  
    testxs.dispose();
  
    console.log("Model evaluated!");
    return [labels, preds];
  }

  function _lowerCaseToCamelCase(str) {
    return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
  }

  

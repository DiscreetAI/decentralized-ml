"use strict";
//exports.__esModule = true;
//var dml_db_js_1 = require("./dml_db.js");
//import { DMLDB } from "./dml_db.js";
// import { DMLRequest } from "./message.js";
import { Runner } from "./runner.js";
import {MnistData} from './assets/data.js';
import {DMLRequest} from "./message.js";
import {DataManager} from "./data_manager.js";
import {DMLDB} from "./dml_db.js";
//var tfjs_1 = require("@tensorflow/tfjs");
//import { loadLayersModel, tensor} from '@tensorflow/tfjs';

//var db = new DMLDB();

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
  const SOCKET_URL = "ws://localhost:8001/";

//     // Runner.sendMessage(request, "Hey Server", SOCKET_URL);
  var ws = new WebSocket(SOCKET_URL);
  var node = 'http://localhost:8002/assets/server'

  ws.onopen = function() {       
      // Web Socket is connected, send data using send()
      // ws.send("Hi Server!");
      //alert("Message is sent...");
    };



// function after_open() {
//     var data = tf.tensor([[1, 2], [3, 4]]).as2D(2, 2);
//     console.log(data.arraySync());
//     db.create("test", data.arraySync(), after_create, "localhost");
// }

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
    array_data.print();
}

function get(yourUrl){
  var Httpreq = new XMLHttpRequest(); // a new request
  Httpreq.open("GET",yourUrl,false);
  Httpreq.send(null);
  return JSON.parsew(Httpreq.responseText);          
}

async function run() {
  // var result = JSON.parse(get(node + "/test/optimizer.json"));
  // console.log(result)
  DMLDB.open(after_open);
  // var data = await getData();
  // var request = DMLRequest.deserialize(JSON.stringify(message));
  // var model = await Runner.getModel(node, "test");
  // const optimization_data = getOptimizationData();
  // model = compileModel(model, optimization_data);
  // model.save('downloads://my-model-1');
  // Runner.train(data, request, model, ws);
  //Runner.handleMessage(request, model, ws);
}

async function after_open() {
  // var data = tf.tensor([[1, 2], [3, 4]]).as2D(2, 2);
  // console.log(data.arraySync());
  // db.create("test", data.arraySync(), after_create, "localhost");
  const data = await getData();
  console.log("Data retrieved!")
  DataManager.store("mnist", data, ws, node);
  console.log("Data stored!");
    //setTimeout(dml, 5000);
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
  Runner.handleMessage(request, model, ws);
  //console.log(data);
  console.log("Success?");
}

  async function getData() {
    const data = new MnistData();
    await data.load();
    console.log("Data loaded!", data);
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

    var xs = trainXs.as2D(TRAIN_DATA_SIZE, 784).arraySync();
    var ys = trainYs.as1D().arraySync();

    //console.log(xs);
    //console.log(ys);

    for (var i = 0; i < ys.length; i++) {
      xs[i].push(ys[i]);
    }  
    //console.log(xs);
    return tf.tensor(xs).as2D(TRAIN_DATA_SIZE, 785);
  }
  
  async function getModel() {
    const MODEL_URL = 'http://localhost:8999/server/model.json';
    const model = await tf.loadLayersModel(MODEL_URL);
    console.log("Model loaded!", model);
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
  
  function _lowerCaseToCamelCase(str) {
    return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
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

document.addEventListener('DOMContentLoaded', run);

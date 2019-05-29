"use strict";

import {MnistData} from './assets/data.js';
import {DataManager} from "./data_manager.js";
import {DMLDB} from "./dml_db.js";

const SOCKET_URL = "ws://localhost:8001/";


var node = 'http://localhost:8002/assets/server'
export const HOST = "99885f00eefcd4107572eb62a5cb429a.au4c4pd2ch.us-west-1.elasticbeanstalk.com";
export const SOCKET_HOST = "ws://" + HOST;
export const FULL_HOST = "http://" + HOST;
var ws = new WebSocket(SOCKET_HOST);
ws.addEventListener("open", function (event) {
  var registrationMessage = {
    "type": "REGISTER",
    "node_type": "LIBRARY"
  }
  ws.send(JSON.stringify(registrationMessage));
});
//const MODEL_URL = node + "/test/model.json";

async function run() {
  console.log("Starting store...")
  DMLDB.open(after_open);
}

async function after_open() {
  const data = await getData();
  console.log("Data retrieved!")
  DataManager.store("mnist", data, ws, HOST);
  console.log("Data stored!");
}

async function getData() {
  const data = new MnistData();
  await data.load();
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

  for (var i = 0; i < ys.length; i++) {
    xs[i].push(ys[i]);
  }  
  return tf.tensor(xs).as2D(TRAIN_DATA_SIZE, 785);
}
  
document.addEventListener('DOMContentLoaded', run);

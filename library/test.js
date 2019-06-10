"use strict";

var DataManager = require('./data_manager.js').DataManager;
var tf = require("@tensorflow/tfjs-node");
const repo_id = "99885f00eefcd4107572eb62a5cb429a";

async function run() {
  DataManager.bootstrap(repo_id);
  console.log("Bootstrapped library!");
  const data = await getData();
  console.log("Data retrieved!");
  DataManager.store("mnist", data);
  console.log("Data stored!");
}

async function getData() {
  var mnist = require('mnist'); // this line is not needed in the browser

  var set = mnist.set(8000, 0);

  var trainingSet = set.training;
  var data = []

  for (var i = 0; i < trainingSet.length; i++) {
    data.push(trainingSet[i].input);
    data[i].push(trainingSet[i].output.indexOf(1));
  }
  return tf.tensor(data).as2D(8000, 785);
}
  
run()

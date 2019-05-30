"use strict";

import {MnistData} from './assets/data.js';
import {DataManager} from "./data_manager.js";
import {DMLDB} from "./dml_db.js";

export const repo_id = "99885f00eefcd4107572eb62a5cb429a";

async function run() {
  DataManager.bootstrap(repo_id);
  console.log("Bootstrapped library!");
  const data = await getData();
  console.log("Data retrieved!")
  DataManager.store("mnist", data);
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

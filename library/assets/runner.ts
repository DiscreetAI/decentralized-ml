import { DMLRequest } from './message.js';
import { DMLDB } from './dml_db.js';
import { LayersModel, Tensor, Tensor2D} from "@tensorflow/tfjs/dist";
import { loadLayersModel, tensor, train} from '@tensorflow/tfjs';
import { TypedArray } from '@tensorflow/tfjs-core/dist/types';

export class Runner {

  static _lowerCaseToCamelCase(str:string) {
    return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
  }
  
  static compileModel(model:LayersModel, optimization_data:any) {
    let optimizer;
    if (optimization_data['optimizer_config']['class_name'] == 'SGD') {
      // SGD
      optimizer = train.sgd(optimization_data['optimizer_config']['config']['lr']);
    } else {
      // Not supported!
      throw "Optimizer not supported!"
    }
  
    model.compile({
      optimizer: optimizer,
      loss: Runner._lowerCaseToCamelCase(optimization_data['loss']),
      metrics: optimization_data['metrics'],
    });
  
    console.log("Model compiled!", model);
    return model;
  }

  static async getModel(node:string,  request:DMLRequest, callback:Function, ws:WebSocket) {
    const model_url:string = "http://" + node + "/model/model.json";
    var model = await loadLayersModel(model_url);
    fetch(model_url)
      .then(res => res.json())
      .then((out) => {
        console.log('Output: ', out);
        model = Runner.compileModel(model, out["modelTopology"]["training_config"]);
        model.save('indexeddb://' + request.id);
        DMLDB.get(request, callback, model, ws);
    }).catch(err => console.error(err));
  }

  static async saveModel(model:LayersModel, path:string) {
    var results = await model.save('indexeddb://' + path);
    console.log("Model saved into IndexedDB! Metadata: ", results);
    return results;
  }
    
  static async getWeights(model:LayersModel) {
    var all_weights = [];
    for (var i = 0; i < model.layers.length * 2; i++) {
      // Time 2 so we can get the bias too.
      let weights = model.getWeights()[i];
      let weightsData = weights.dataSync();
      let weightsList = Array.from(weightsData);
      for (var j = 0; j < weightsList.length; j++) {
        all_weights.push(weightsList[j]);
      }
    }
    return all_weights;
  }
    

  static labelData(data:number[][], label_index:number):Tensor[] {
    if (label_index < 0) {
        label_index = data[0].length - 1;
    }
    var trainXs:number[][] = data;
    var trainYs:number[] = trainXs.map(row => row[label_index]);
    trainXs.forEach(function(x) {x.splice(label_index, 1)});
    return [tensor(trainXs), tensor(trainYs)]
  }

  static async train(data:Tensor2D, request:DMLRequest, model:LayersModel, ws:WebSocket) {
    var [data_x, data_y] = Runner.labelData(data.arraySync(), request.params.label_index);
    model.fit(data_x, data_y, {
      batchSize: request.params["batch_size"],
      epochs: request.params["epochs"],
      shuffle: request.params["shuffle"]
    });
    console.log("Finished training!");
    await Runner.saveModel(model, request.id);
    var weights = await Runner.getWeights(model)
    var results = {
      "weights": weights,
      "omega": data.arraySync().length
    }
    console.log("Training results:")
    console.log(results);
    DMLDB.put(request, Runner.sendMessage, results, ws);     
  }

  static async evaluate(data:Tensor2D, request:DMLRequest, model:LayersModel, ws:WebSocket) {
    var [data_x, data_y] = Runner.labelData(data.arraySync(), request.params.label_index);
    var result:string = model.evaluate(data_x, data_y).toString();
    DMLDB.put(request, Runner.sendMessage, result, ws);
  }

  static async sendMessage(request:DMLRequest, message:string, ws:WebSocket) {
    var result:string = DMLRequest.serialize(request, message);
    ws.send(result);
  }

  static async handleMessage(request:DMLRequest, node:string, ws:WebSocket) {
    var callback:Function = (request.action == 'TRAIN') ? Runner.train : Runner.evaluate;
    await Runner.getModel(node, request, callback, ws); 
  }
}
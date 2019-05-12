import { DMLRequest } from './message.js';
import { DMLDB } from './dml_db.js';
import { LayersModel, Tensor, Tensor2D} from "@tensorflow/tfjs/dist";
import { loadLayersModel, tensor, train} from '@tensorflow/tfjs';
import { TypedArray } from '@tensorflow/tfjs-core/dist/types';

export class Runner {

    // static async getModel() {
    //     const MODEL_URL = 'http://localhost:5000/server/model.json';
    //     const model: LayersModel = await loadLayersModel(MODEL_URL);
    //     console.log("Model loaded!", model);
    //     return model;
    // }
    
    static getOptimizationData(url:string) {
        var Httpreq = new XMLHttpRequest(); // a new request
        Httpreq.open("GET",url,false);
        Httpreq.send(null);
        return JSON.parse(Httpreq.responseText);
    }

    static _lowerCaseToCamelCase(str:string) {
        return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
      }
    
    static async compileModel(model:LayersModel, optimization_data:any) {
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
    static async getModel(node:string,  id:string) {
        const request_url:string = node + "/" + id;
        const model_url:string = request_url + '/model.json';
        const optimizer_url = request_url + "/optimizer.json";
        //console.log("Retrieving model from: " + MODEL_URL);
        const model = await loadLayersModel(model_url);
        const optimization_data = await Runner.getOptimizationData(optimizer_url);;
        Runner.compileModel(model, optimization_data);
        //console.log("Model loaded!", model);
        return model;
    }

    static async saveModel(model:LayersModel, path:string) {
        var results = await model.save('indexeddb://' + path);
        console.log("Model saved into IndexedDB! Metadata: ", results);
        return results;
    }
      
    static async getWeights(path:string) {
        try {
          var model:any = await Runner.getLocalModel(path);
          return model["modelArtifacts"]["weightData"];
        } catch(err) {
          console.log(err);
          return null;
        }
    }
      
    static getLocalModel(path:string) {
        return new Promise(function (resolve, reject) {
          var openRequest = indexedDB.open("tensorflowjs",1);
          openRequest.onsuccess = function() {
              var db = openRequest.result;
              var tx = db.transaction('models_store', 'readonly');
              var store = tx.objectStore('models_store');
              var request = store.get(path);
              request.onsuccess = function() {
                resolve(request.result);
              }
      
              request.onerror = function(e) { reject(e) }
      
              tx.oncomplete = function() { db.close(); }
          };
          openRequest.onerror = function(e) { reject(e) }
        });
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
        var [data_x, data_y] = Runner.labelData(data.arraySync(), request.label_index);
        model.fit(data_x, data_y, {
            batchSize: request.params["batch_size"],
            epochs: request.params["epochs"],
            shuffle: request.params["shuffle"]
          });
          //await Runner.saveModel(model, request.id);
          //var weights = await Runner.getWeights(request.id)
          var weightsTensor:Tensor[] = model.getWeights();
          var weights:TypedArray[] = [];
          for (var i = 0; i < weightsTensor.length; i++) {
            var item:TypedArray = await weightsTensor[i].data();
            weights.push(item);
          }
          Runner.sendMessage(request, JSON.stringify(weights), ws);
          
    }

    static async evaluate(data:Tensor2D, request:DMLRequest, model:LayersModel, ws:WebSocket) {
        var [data_x, data_y] = Runner.labelData(data.arraySync(), request.label_index);
        var result:string = model.evaluate(data_x, data_y).toString();
        Runner.sendMessage(request, result, ws);
    }

    static async sendMessage(request:DMLRequest, message:string, ws:WebSocket) {
        var result:string = DMLRequest.serialize(request, message);
        ws.send(result);
        //TODO: Send weights to node
    }

    static async handleMessage(request:DMLRequest, node:string, ws:WebSocket) {
        var model:LayersModel = await Runner.getModel(node, request.id);
        Runner.saveModel(model, request.id);
        var callback:Function = (request.action == 'train') ? Runner.train : Runner.evaluate;
        DMLDB.get(request, callback, model, ws);
    }
}
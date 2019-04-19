import { DMLRequest } from './message.js';
import { DMLDB } from './dml_db.js';
import { LayersModel, Tensor, Tensor2D, train } from "@tensorflow/tfjs/dist";
import { loadLayersModel, tensor} from '@tensorflow/tfjs';
import * as tf from '@tensorflow/tfjs';

export class Runner {

    static async getModel() {
        const MODEL_URL = 'http://localhost:5000/server/model.json';
        const model: LayersModel = await loadLayersModel(MODEL_URL);
        console.log("Model loaded!", model);
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

    static async train(data:Tensor2D, request:DMLRequest, model:LayersModel, node:string) {
        var [data_x, data_y] = Runner.labelData(data.arraySync(), request.label_index);
        model.fit(data_x, data_y, {
            batchSize: request.params["batch_size"],
            epochs: request.params["epochs"],
            shuffle: request.params["shuffle"]
          });
          Runner.saveModel(model, request.id);
          var weights = Runner.getWeights(request.id)
          Runner.sendMessage(request, JSON.stringify(weights), node);
          
    }

    static async evaluate(data:Tensor2D, request:DMLRequest, model:LayersModel, node:string) {
        var [data_x, data_y] = Runner.labelData(data.arraySync(), request.label_index);
        var result:string = model.evaluate(data_x, data_y).toString();
        Runner.sendMessage(request, result, node);
    }

    static async sendMessage(request:DMLRequest, message:string, node:string) {
        var result:string = DMLRequest.serialize(request, message);
        var serverSocket:WebSocket = new WebSocket(node);
        serverSocket.send(result);
        //TODO: Send weights to node
    }

    static async handleMessage(request:DMLRequest, db:DMLDB, node:string) {
        var model:LayersModel = await Runner.getModel();
        Runner.saveModel(model, request.id);
        var callback:Function = (request.action == 'train') ? Runner.train : Runner.evaluate;
        db.get(request, callback, model, node);
    }
}
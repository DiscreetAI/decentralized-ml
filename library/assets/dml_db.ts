import { Tensor, Tensor2D, LayersModel, tensor } from "@tensorflow/tfjs";
import { DMLRequest } from "./message.js";
import { getRowsCols } from "@tensorflow/tfjs-core/dist/kernels/webgl/webgl_util";

export class DMLDB {
  static datastore: any;

  static _open() {
    // Database version.
    var version = 1;
  
    // Open a connection to the datastore.
    var request = indexedDB.open('datamappings', version);
  
    // Handle datastore upgrades.
    request.onupgradeneeded = function(e:any) {
      var db = e.target.result;
  
      //e.target.transaction.onerror = tDB.onerror;
  
      // Delete the old datastore.
      if (db.objectStoreNames.contains('datamapping')) {
        db.deleteObjectStore('datamapping');
      }
  
      // Create a new datastore.
      var store = db.createObjectStore('datamapping', {
        keyPath: 'repo'
      });
    };
  
    // Handle successful datastore access.
    request.onsuccess = function(e:any) {
      // Get a reference to the DB.
      DMLDB.datastore = e.target.result;
  
      // Execute the callback.
      console.log("DMLDB successfully opened!");
    };
  
    // Handle errors when opening the datastore.
    //request.onerror = this.onerror;
  };

  static _create(repo:string, data:number[][], callback:Function) {
    // Get a reference to the db.
    var db = DMLDB.datastore;
  
    // Initiate a new transaction.
    var transaction = db.transaction(['datamapping'], 'readwrite');
  
    // Get the datastore.
    var objStore = transaction.objectStore('datamapping');
  
    // Create a timestamp for the data item.
    var timestamp = new Date().getTime();
  
    // Create an object for the data item.
    var datamapping = {
      'data': data,
      'rows': data.length,
      'cols': data[0].length,
      'repo': repo,
      'timestamp': timestamp, 
      'sessions': {}
    };
  
    // Create the datastore request.
    var request = objStore.put(datamapping);
    // Handle a successful datastore put.
    request.onsuccess = function(e:any) {
      // Execute the callback function.
      callback();
    };
  
    // Handle errors.
    //request.onerror = tDB.onerror;
  };

  static _create_session(data:Tensor2D, dml_request:DMLRequest, callback:Function, 
    model:LayersModel, datamapping:any) {
    // Get a reference to the db.
    var db = DMLDB.datastore;
  
    // Initiate a new transaction.
    var transaction = db.transaction(['datamapping'], 'readwrite');
  
    // Get the datastore.
    var objStore = transaction.objectStore('datamapping');
  
    // Create an object for the data item.
    var session = {
      'round': 0
    };
    datamapping.sessions[dml_request.id] = session;
  
    // Create the datastore request.
    var request = objStore.put(datamapping);
    // Handle a successful datastore put.
    request.onsuccess = function(e:any) {
      // Execute the callback function.
      callback(data, dml_request, model);
    };
  
    // Handle errors.
    //request.onerror = tDB.onerror;
  };

  static _get(dml_request:DMLRequest, callback:Function, model:LayersModel) {
    var db = DMLDB.datastore;
    var transaction = db.transaction(['datamapping'], 'readwrite');
    var objStore = transaction.objectStore('datamapping');
  
    var request = objStore.get(dml_request.repo);
  
    request.onsuccess = function(e:any) {
      var data = tensor(request.result.data).as2D(request.result.rows, request.result.cols);
      if (dml_request.action == 'TRAIN') {
        var sessions = request.result.sessions;
        if (!(dml_request.id in sessions)) {
          DMLDB._create_session(data, dml_request, callback, model, request.result);
          return;
        }
        var session_entry = sessions[dml_request.id];
        if (session_entry.round + 1 != dml_request.round) {
          console.log("Ignoring server's message...");
          console.log("Request's round was " + dml_request.round + " and current round is " + session_entry.round);
          return;
        } 
      }
      callback(data, dml_request, model);
    }
  
    request.onerror = function(e:any) {
      console.log(e);
    }
  };

  static _put(dml_request:DMLRequest, callback:Function, result:any) {
    var db = DMLDB.datastore;
    var transaction = db.transaction(['datamapping'], 'readwrite');
    var objStore = transaction.objectStore('datamapping');
  
    var request = objStore.get(dml_request.repo);
  
    request.onsuccess = function(e:any) {
      request.result.sessions[dml_request.id].round = dml_request.round;
      callback(dml_request, result);
    }
  
    request.onerror = function(e:any) {
      console.log(e);
    }
  };
}
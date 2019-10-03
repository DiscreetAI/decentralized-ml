exports.__esModule = true;
var DMLRequest = require("./message.js").DMLRequest;
var DMLDB = require("./dml_db.js").DMLDB;
var DataManager = require("./data_manager.js").DataManager;
var tfjs_1 = require("@tensorflow/tfjs-node");
var fetch = require('node-fetch');

class Runner {
    static _lowerCaseToCamelCase = function (str) {
        return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
    };
    static _compileModel(model, optimization_data) {
        var optimizer;
        
        if (optimizer_config['class_name'] == 'SGD') {
            // SGD
            optimizer = tfjs_1.train.sgd(optimizer_config['config']['lr']);
        } else if (optimization_data['optimizer_config']['class_name'] == 'Adam') {
            optimizer = tfjs_1.train.adam(optimizer_config['config']['lr'], optimizer_config['config']['beta1'], optimizer_config['config']['beta2'])
        } else {
            // Not supported!
            throw "Optimizer not supported!";
        }
        model.compile({
            optimizer: optimizer,
            loss: Runner._lowerCaseToCamelCase(optimization_data['loss']),
            metrics: optimization_data['metrics']
        });
        console.log("Model compiled!", model);
        return model;
    }

    static async _getModel(request, callback) {
        const model_url = DataManager.cloud_url + "/model/model.json";
        var model = await loadLayersModel(model_url);
        fetch(model_url)
        .then(res => res.json())
        .then((out) => {
            console.log('Output: ', out);
            model = Runner._compileModel(model, out["modelTopology"]["training_config"]);
            Runner._saveModel(model, request.id);
            DMLDB._get(request, callback, model);
        }).catch(err => console.error(err));
    }

    static async _getWeights(model) {
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
    };

    static _labelData(data, label_index) {
        if (label_index < 0) {
            label_index = data[0].length - 1;
        }
        var trainXs = data;
        var trainYs = trainXs.map(function (row) { return row[label_index]; });
        trainXs.forEach(function (x) { x.splice(label_index, 1); });
        return [tfjs_1.tensor(trainXs), tfjs_1.tensor(trainYs)];
    };

    static async _train(data, request, model) {
        var [data_x, data_y] = Runner._labelData(data.arraySync(), request.params.label_index);
        model.fit(data_x, data_y, {
            batchSize: request.params["batch_size"],
            epochs: request.params["epochs"],
            shuffle: request.params["shuffle"]
        });
        console.log("Finished training!");
        await Runner._saveModel(model, request.id);
        var weights = await Runner._getWeights(model)
        var results = {
            "weights": weights,
            "omega": data.arraySync().length
        }
        console.log("Training results:")
        console.log(results);
        DMLDB._put(request, Runner._sendMessage, results); 
    }

    static async _evaluate(data, request, model) {
        var [data_x, data_y] = Runner._labelData(data.arraySync(), request.params.label_index);
        var result = model.evaluate(data_x, data_y).toString();
        DMLDB._put(request, Runner._sendMessage, result);
    }

    static async _sendMessage(request, message) {
        var result = DMLRequest._serialize(request, message);
        DataManager.ws.send(result);
    }

    static async _handleMessage(request) {
        var callback = (request.action == 'TRAIN') ? Runner._train : Runner._evaluate;
        await Runner._getModel(request, callback); 
    }
}

exports.Runner = Runner;

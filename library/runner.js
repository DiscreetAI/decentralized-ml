"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
var message_js_1 = require("./message.js");
var tfjs_1 = require("@tensorflow/tfjs");
var Runner = /** @class */ (function () {
    function Runner() {
    }
    Runner.getModel = function () {
        return __awaiter(this, void 0, void 0, function () {
            var MODEL_URL, model;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        MODEL_URL = 'http://localhost:5000/server/model.json';
                        return [4 /*yield*/, tfjs_1.loadLayersModel(MODEL_URL)];
                    case 1:
                        model = _a.sent();
                        console.log("Model loaded!", model);
                        return [2 /*return*/, model];
                }
            });
        });
    };
    Runner.saveModel = function (model, path) {
        return __awaiter(this, void 0, void 0, function () {
            var results;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, model.save('indexeddb://' + path)];
                    case 1:
                        results = _a.sent();
                        console.log("Model saved into IndexedDB! Metadata: ", results);
                        return [2 /*return*/, results];
                }
            });
        });
    };
    Runner.getWeights = function (path) {
        return __awaiter(this, void 0, void 0, function () {
            var model, err_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        return [4 /*yield*/, Runner.getLocalModel(path)];
                    case 1:
                        model = _a.sent();
                        return [2 /*return*/, model["modelArtifacts"]["weightData"]];
                    case 2:
                        err_1 = _a.sent();
                        console.log(err_1);
                        return [2 /*return*/, null];
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    Runner.getLocalModel = function (path) {
        return new Promise(function (resolve, reject) {
            var openRequest = indexedDB.open("tensorflowjs", 1);
            openRequest.onsuccess = function () {
                var db = openRequest.result;
                var tx = db.transaction('models_store', 'readonly');
                var store = tx.objectStore('models_store');
                var request = store.get(path);
                request.onsuccess = function () {
                    resolve(request.result);
                };
                request.onerror = function (e) { reject(e); };
                tx.oncomplete = function () { db.close(); };
            };
            openRequest.onerror = function (e) { reject(e); };
        });
    };
    Runner.labelData = function (data, label_index) {
        if (label_index < 0) {
            label_index = data[0].length - 1;
        }
        var trainXs = data;
        var trainYs = trainXs.map(function (row) { return row[label_index]; });
        trainXs.forEach(function (x) { x.splice(label_index, 1); });
        return [tfjs_1.tensor(trainXs), tfjs_1.tensor(trainYs)];
    };
    Runner.train = function (data, request) {
        var _a = Runner.labelData(data.arraySync(), request.label_index), data_x = _a[0], data_y = _a[1];
        request.model.fit(data_x, data_y, {
            batchSize: request.params["batch_size"],
            epochs: request.params["epochs"],
            shuffle: request.params["shuffle"]
        });
        Runner.saveModel(request.model, request.id);
        Runner.sendMessage(new message_js_1.DMLResult(request.id, request.repo, request.type, Runner.getWeights(request.id)));
    };
    Runner.evaluate = function (data, request) {
        var _a = Runner.labelData(data.arraySync(), request.label_index), data_x = _a[0], data_y = _a[1];
        Runner.sendMessage(new message_js_1.DMLResult(request.id, request.repo, request.type, request.model.evaluate(data_x, data_y)));
    };
    Runner.sendMessage = function (result) {
        //TODO: Send weights to node
    };
    Runner.handleMessage = function (request, db) {
        return __awaiter(this, void 0, void 0, function () {
            var model, result, callback;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, Runner.getModel()];
                    case 1:
                        model = _a.sent();
                        Runner.saveModel(model, request.id);
                        callback = (request.type == 'train') ? Runner.train : Runner.evaluate;
                        db.get(request, callback);
                        return [2 /*return*/];
                }
            });
        });
    };
    return Runner;
}());
exports.Runner = Runner;

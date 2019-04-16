import {
  getData,
  getModelFromCloud,
  getValidationAccuracy,
  compileModel,
  getOptimizationData,
  retrainModel,
  makeUpdateObject,
} from './script2.js';

const SOCKET_URL = "ws://localhost:8999/"

let socket = new WebSocket(SOCKET_URL);

socket.onopen = (e) => {
  //socket.send("Just saying hi!");
  console.log("Connected to cloud node!");
  socket.send(
    JSON.stringify({"type": "REGISTER", "node_type": "library"})
  );
}

socket.onmessage = async function onmessage(e) {
  var json_data = JSON.parse(e.data);
  console.log("Update received! (instructions)", json_data);

  // Checks
  if (!("action" in json_data)) {
    return;
  }

  if (json_data["action"] == "TRAIN") {
    // Train the model and send updates once complete.
    let session_id = json_data["session_id"];
    let round = json_data["round"];

    var model = await getModelFromCloud();
    let data = await getData();

    let accuracy = await getValidationAccuracy(model, data);

    let optimization_data = getOptimizationData();
    model = compileModel(model, optimization_data);

    let batch_size = json_data["hyperparams"]["batch_size"];
    let epochs = json_data["hyperparams"]["epochs"];
    await retrainModel(model, data, epochs, batch_size);
    let new_accuracy = await getValidationAccuracy(model, data);

    makeUpdateObject(session_id, round, model, new_accuracy).then((update) => {
      socket.send(JSON.stringify(update));
      console.log("Update sent! (new weights)", update);
    })
  }

  // Send an update to the server!
  // makeMockUpdateForCloudNode(session_id, round).then( (update) => {
  //   socket.send(JSON.stringify(update));
  //   console.log("Update sent! (new weights)", update);
  // });
}

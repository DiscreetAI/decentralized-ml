import {
  SOCKET_HOST,
  getData,
  getModelFromCloud,
  getValidationAccuracy,
  compileModel,
  getOptimizationData,
  retrainModel,
  makeUpdateObject,
} from './script2.js';

function makeSocket(current_round) {
  let socket = new WebSocket("ws://" + SOCKET_HOST);

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
    if (!("action" in json_data) || json_data["round"] <= current_round) {
      console.log("Ignoring...")
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
        tryToUpdateCloudNodeUntilItWorks(update);
      })
    }
  }

  return socket;
}

async function tryToUpdateCloudNodeUntilItWorks(update) {
  // var success = false;

  console.log(socket.readyState, socket.OPEN);
  socket.send(JSON.stringify(update));

  while (socket.readyState != socket.OPEN) {
    console.log("Failed at sending update... Retrying...");
    await sleep(2000);
    socket = makeSocket(update["round"]);
    await sleep(5000); // This should instead wait until the websocket is
                       // reconnected.
    socket.send(JSON.stringify(update));
  }

  console.log("Update sent! (new weights)", update);

  // do {
  //   console.log(socket.readyState);
  //   console.log(socket.OPEN);
  //   try {
  //     socket.send(JSON.stringify(update));
  //     success = true;
  //   } catch(err) {
  //     console.log("Failed at sending update... Retrying...", err);
  //     socket = new WebSocket("ws://" + SOCKET_HOST);
  //     await sleep(5000); // This should instead wait until the websocket is
  //                        // reconnected.
  //     success = false;
  //   }
  // } while (!success);

  // if (success) {
  //   console.log("Update sent! (new weights)", update);
  // } else {
  //   console.log("Not sure what happened.");
  // }

}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

let socket = makeSocket(0);

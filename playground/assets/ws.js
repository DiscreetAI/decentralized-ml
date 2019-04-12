import {makeMockUpdateForCloudNode} from './script2.js';

const SOCKET_URL = "ws://localhost:8999/"

let socket = new WebSocket(SOCKET_URL);

socket.onopen = (e) => {
  //socket.send("Just saying hi!");
  console.log("Connected to cloud node!");
}

socket.onmessage = (e) => {
  var json_data = JSON.parse(e.data);
  console.log("Update received! (instructions)", json_data);

  // Checks
  if (!("action" in json_data)) {
    return;
  }

  // Send an update to the server!
  var session_id = json_data["session_id"];
  var round = json_data["round"];
  makeMockUpdateForCloudNode(session_id, round).then( (update) => {
    socket.send(JSON.stringify(update));
    console.log("Update sent! (new weights)", update);
  });

}

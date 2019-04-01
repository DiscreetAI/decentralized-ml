import * as WebSocket from 'ws';
import * as http from 'http';
import { app } from './endpoints';

let WSServer = WebSocket.Server;
let server = http.createServer();

let wss = new WSServer({ server: server }); // Create WS server on top of HTTP.

server.on('request', app); // Mount the app.

wss.on('connection', function connection(ws) {

  ws.on('message', function incoming(message) {
    console.log(`Received: ${message}`);
    ws.send(JSON.stringify({ answer: 42 }));
  });

  console.log("New connection!");
  ws.send(JSON.stringify({message: "new connection"}));
});

server.listen(process.env.PORT, function() {
  console.log(`http/ws server listening on ${process.env.PORT}`);
});

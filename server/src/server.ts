import * as express from 'express';
import * as http from 'http';
import * as WebSocket from 'ws';

const app = express();

// app.get('/new', (req, res) => {
//   console.log("Starting DML Session...");
//   res.end("Starting DML Session...");
// })

//initialize a simple http server
const server = http.createServer(app);

//initialize the WebSocket server instance
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws: WebSocket) => {

    //connection is up, let's add a simple simple event
    ws.on('message', (message: string) => {

        //log the received message and send it back to the client
        console.log('received: %s', message);
        ws.send(`Hello, you sent -> ${message}`);
    });

    //send immediatly a feedback to the incoming connection
    ws.send('Hi there, I am a WebSocket server');
});

//start our server
const PORT: any = process.env.PORT || 8999;
server.listen(PORT, () => {
    console.log(`Server started on port ${PORT} :)`);
});

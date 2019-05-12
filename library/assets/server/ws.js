var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('Hello World!');
}).listen(8080);

var WebSocketServer = require('ws').Server,
ws = new WebSocketServer({port: 8001})

connections = []
ws.on('connection', function(w){
    connections.push(w)
    // var id = w.upgradeReq.headers['sec-websocket-key'];
    // console.log('New Connection id :: ', id);
    // w.send(id);
    w.send("Hi Client!");
    console.log("Connected with client!");
    w.on('message', function(msg){
        //var id = w.upgradeReq.headers['sec-websocket-key'];
        console.log("Client sent us weights!");
    });
    var timer = setTimeout(sendMessage, 10000);
    w.on('close', function() {
        //var id = w.upgradeReq.headers['sec-websocket-key'];
    });

    //sockets[id] = w;
});

function sendMessage() {
    console.log("Sending messages!");
    for (var i = 0; i < connections.length; i++) {
        var params = {
            "batch_size": 8000,
            "epochs": 5,
            "shuffle": true
          }
        var message = {
            "id": "test",
            "repo": "mnist",
            "action": "train",
            "params": params,
            "label_index": 0
        }
        connections[i].send(JSON.stringify(message));
    }
}





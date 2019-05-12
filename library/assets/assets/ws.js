const SOCKET_URL = "ws://localhost:8999/"
let socket = new WebSocket(SOCKET_URL);

socket.onopen = (e) => {
  socket.send("Just saying hi!");
}

socket.onmessage = (e) => {
  console.log(e.data);
}

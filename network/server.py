import argparse
import socket
from color_utils import *


class Server(object):
    def __init__(self, host, port, protocol='tcp'):
        self.clients = {}
        self.order = []
        self.files = []
        self.online = False
        self.protocol = protocol
        self.sock = socket.socket()
        try:
            self.sock.bind((host, port))
            self.host = host
            self.port = port
            self.online = True
        except ConnectionRefusedError:
            print("Connection refused...")
            exit(1)

    def listen(self, limit=5):
        assert(self.online)
        message = "..."
        self.sock.listen(limit)
        while True:
            c = None
            print("Listening...")
            try:
                c, addr = self.sock.accept()
                gprint("Got connection from", addr)
                message = self.ret_msg(c)
                response = self.process(addr, message)
                self.respond(c, response)
                c.close()
            except KeyboardInterrupt:
                # The following may be useful, `ps -fA | grep python`
                rprint("\nKeyboardInterrupt...\nSocket closed.")
                if c:
                    c.close()
                break

    def process(self, addr, m):
        self.clients[addr] = m
        self.order.append(addr)
        if m == 'PING':
            return 'PONG'
        elif m.split(' ')[0] == 'QUERY':
            if m.split(' ')[1] in self.files:
                return 'QUERYHIT'
            else:
                return 'NOT FOUND'
        else:
            return 'hello, World!'

    def respond(self, sock, m):
        assert(type(m) == str)
        bprint("Sending message: ", m)
        sock.send(m.encode())

    def ret_msg(self, sock):
        assert(self.online)
        message = sock.recv(1024).decode('utf-8')
        gprint("Received message: ", message)
        return message

    def close(self):
        assert(self.online)
        self.sock.close()
        self.online = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help="specify a port number \
        (defaults to 12345)")
    args = parser.parse_args()
    p = args.port if args.port else 12345
    ip = socket.gethostbyname('localhost')
    print(ip)
    sock = Server(ip, p)
    sock.listen()
    sock.close()

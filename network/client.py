import argparse
import socket
from color_utils import *


class Client(object):
    def __init__(self, host, port, protocol='tcp'):
        self.peers = []
        self.online = False
        self.protocol = protocol
        self.sock = socket.socket()
        try:
            self.sock.connect((host, port))
            self.host = host
            self.port = port
            self.online = True
        except ConnectionRefusedError:
            print("Connection refused...")
            exit(1)

    def push(self, m):
        assert(type(m) == str)
        bprint("Sending message: ", m)
        self.sock.send(m.encode())

    def get_msg(self):
        assert(self.online)
        message = self.sock.recv(1024).decode('utf-8')
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
    parser.add_argument('-m', '--message', type=str, help="specify a \
        message to send")
    args = parser.parse_args()
    p = args.port if args.port else 12345
    m = args.message if args.message else 'PING'
    sock = Client("127.0.0.1", p)
    sock.push(m)
    sock.get_msg()
    sock.close()

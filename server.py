#!/usr/bin/env python

import socket
import threading

print("Test")

TCP_IP = '127.0.0.1'
TCP_PORT = 52585 # OS will pick a free port
BUFFER_SIZE = 1234

class Server(threading.Thread):
    def __init__(self, conn):
        super(Server, self).__init__() 
        self.conn = conn
    def run(self):
        while 1:
            data = self.conn.recv(BUFFER_SIZE)
            if not data: break
            print("received data: " + data.decode('utf-8'))
            self.conn.send("Hello world 2".encode('utf-8'))  # echo
        self.conn.close()

class SocketHandler(threading.Thread):

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((TCP_IP, TCP_PORT))
        self.s.listen(1)
        while True:

            conn, addr = self.s.accept()
            global threads
            Server(conn).start()
            print('Connection address: ' + addr[0])


def main():

    t1 = SocketHandler()
    t1.start()

    t1.join()

    # threads = [t1]

    # for t in threads:
    #     t.start()

    # for t in threads:
    #     t.join()

main()

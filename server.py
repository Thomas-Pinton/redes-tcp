import socket
import threading
import time
import constants as c
from hashlib import sha256
import struct


TCP_IP = '127.0.0.1'
TCP_PORT = 0 # OS will pick a free port
BUFFER_SIZE = 1234

class Server(threading.Thread):

    def __init__(self, conn, id):
        super(Server, self).__init__() 
        self.conn = conn
        self.id = id
        self.data = ''

    def run(self):
        while 1:
            data = self.conn.recv(BUFFER_SIZE)
            if data:
                self.data = data.decode('utf-8')
                print("-- received data --")
                print("   connection id: " + str(self.id))
                print("   data: " + self.data)

                self.data = self.data.split()

                if int(self.data[0]) == int(c.LEAVE):
                    print("   closing connection id: " + str(self.id))
                    break
                else:
                    self.handleData()
            #     self.conn.send(data)  # echo
        self.conn.close()


    def getFile(self, filename):
        with open("media/" + filename,"rb") as f:
            bytes = f.read() # read entire file as bytes
            hash = sha256(bytes)
            return bytes, hash

    def handleData(self):
        print(self.data)
        print(self.data[0])
        print(c.REQUEST_FILE)
        if (int(self.data[0]) == c.REQUEST_FILE):
            print("   file requested: " + self.data[1])
            file, hash = self.getFile(self.data[1])
            print("File SHA-256: " + hash.hexdigest())
            # print(file[0])
            # print(file[1])
            # print(file[2])
            print(len(file))

            self.conn.send( bytes([c.SEND_FILE_START]) + struct.pack("!Q", len(file)) ) # TODO colocar metadados
            time.sleep(0.01)

            pos = 0
            self.conn.send( file )
            # while pos + c.CHUNK_SIZE < len(file):
            #     chunk = file[pos: pos + c.CHUNK_SIZE]
            #     self.conn.send( chunk )
            #     pos += c.CHUNK_SIZE

            # self.conn.send( bytes([c.SEND_FILE_END]) ) 
            print("File sent")


class SocketHandler(threading.Thread):

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((TCP_IP, TCP_PORT))
        print("Listening on: ", self.s.getsockname())

        with open("port.txt", "w") as file:
            file.write(str(self.s.getsockname()[1]) + "\n")

        self.s.listen(1)
        id = 0    
    
        while True:
            conn, addr = self.s.accept()
            global threads
            Server(conn, id).start()
            id += 1
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

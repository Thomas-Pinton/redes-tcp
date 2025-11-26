import socket
import threading
import time
import constants as c
from hashlib import sha256
import struct
import os


TCP_IP = '127.0.0.1'
TCP_PORT = 0 # OS will pick a free port
BUFFER_SIZE = 1234

threads = []

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
        path = os.path.join("media", filename)

        if not os.path.exists(path):
            self.conn.send( bytes([c.SEND_FILE_NOT_FOUND]) )
            return None, None

        with open("media/" + filename,"rb") as f:
            fileBytes = f.read() # read entire file as bytes
            hash = sha256(fileBytes)
            return fileBytes, hash

    def handleData(self):
        print(self.data)
        print(self.data[0])
        print(c.REQUEST_FILE)

        if (int(self.data[0]) == c.REQUEST_FILE):
            print("   file requested: " + self.data[1])

            file, hash = self.getFile(self.data[1])
            if file is None:
                print("File not found")
                return

            print("File SHA-256: " + hash.hexdigest())
            print(len(file))

            self.conn.send( bytes([c.SEND_FILE_START]) + struct.pack("!Q", len(file)) + hash.digest() ) 
            time.sleep(0.01)

            self.conn.send( file )
            print("File sent")

        elif (int(self.data[0]) == c.SEND_CHAT):
            chat_message = ' '.join(self.data[1:])
            print("   chat message received: " + chat_message)


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
            thread = Server(conn, id)
            thread.start()
            threads.append(thread)
            id += 1
            print('Connection address: ' + addr[0])


class InputHandler(threading.Thread):
    def run(self):
        while True:
            message = input("Send a message: ")
            print("You entered: " + message)
            global threads
            for t in threads:
                if t.is_alive():
                    t.conn.send(bytes([c.SEND_CHAT]) + message.encode('utf-8') )


def main():

    t1 = SocketHandler()
    t2 = InputHandler()

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # threads = [t1]

    # for t in threads:
    #     t.start()

    # for t in threads:
    #     t.join()

main()

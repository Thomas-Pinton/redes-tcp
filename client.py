#!/usr/bin/env python

import socket
import sys
import constants as c
from hashlib import sha256
from pathlib import Path
import struct

TCP_IP = '127.0.0.1'
TCP_PORT = 0

#Getting TCP port
if (sys.argv.__len__() < 2):
    with open("port.txt", "r") as file:
        TCP_PORT = int(file.read())
else:
    TCP_PORT = int(sys.argv[1])

BUFFER_SIZE = 1234
# MESSAGE = str(c.SEND_CHAT) + " Hello, World!"
message = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
# s.send(MESSAGE.encode('utf-8'))
# data = s.recv(BUFFER_SIZE)

def getFile(filename):
    with open("media/" + filename,"rb") as f:
        bytes = f.read() # read entire file as bytes
        hash = sha256(bytes)
        return bytes, hash
    
def writeFile(data):
    byte_data = data
    Path("media/received/" + targetFile).write_bytes(byte_data)   

targetFile = "foto2.jpg"

def recv_exact(s, n):
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if chunk:
            data += chunk
    return data


while True:

    message = input("Enter a command: ")

    message = message.split()
    message[0] = message[0].lower()

    if message[0] == "leave":
        message = str(c.LEAVE)
    elif message[0] == "file":
        if message.__len__() < 2:
            message = str(c.REQUEST_FILE) + " " + targetFile
        else:
            message = str(c.REQUEST_FILE) + " " + message[1]
            targetFile = message[1]

    if message != '':
        s.send(message.encode('utf-8'))
        if message == str(c.LEAVE):
            print("Closing connection.")
            break

    file = b''
    fileSize = 0
    totalReceived = 0

    data = recv_exact(s, 9)

    if int(data[0]) == c.SEND_FILE_START:
        fileSize = struct.unpack("!Q", data[1:9])[0]
        print("File size: ", fileSize)

    while True:
        data = s.recv(BUFFER_SIZE)
        if data:
            # if int(data[0]) == c.SEND_FILE:
            file += bytes(data)
            totalReceived += len(data)
            print(totalReceived)
            # print("Receiving file")
            # print("Chunk size: ", len(data[1:]))
            # elif int(data[0]) == c.SEND_FILE_END:
            #     print("File received")
            #     writeFile(file)
            #     break
        if fileSize == totalReceived:
            print("File received")
            writeFile(file)
            break

            
s.close()
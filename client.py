import socket
import sys
import constants as c
from hashlib import sha256
from pathlib import Path
import struct
import threading

TCP_IP = '127.0.0.1'
TCP_PORT = 0
BUFFER_SIZE = 1234

targetFile = "foto2.jpg"

command = ''

endConnection = False

#Getting TCP port
if (sys.argv.__len__() < 2):
    with open("port.txt", "r") as file:
        TCP_PORT = int(file.read())
else:
    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.settimeout(1)

def getFile(filename):
    with open("media/" + filename,"rb") as f:
        bytes = f.read() # read entire file as bytes
        hash = sha256(bytes)
        return bytes, hash
    
def writeFile(data):
    global targetFile
    byte_data = data
    Path("media/received/" + targetFile).write_bytes(byte_data)   


def recv_exact(s, n):
    data = b""
    while len(data) < n:
        try:
            chunk = s.recv(n - len(data))
            if chunk:
                data += chunk
            else:
                return None
        except socket.timeout:
            return None
    return data

def handleSendFile():
    file = b''
    fileSize = 0
    hash = ''
    totalReceived = 0
    fileSize = struct.unpack("!Q", recv_exact(s, 8))[0]
    print("File size: ", fileSize)

    hash = recv_exact(s, 32)

    while True:
        data = s.recv(BUFFER_SIZE)
        if data:
            file += bytes(data)
            totalReceived += len(data)
            print(totalReceived)

        if fileSize == totalReceived:
            print("File received")
            print("File SHA-256: " + sha256(file).hexdigest())
            break

    if hash == sha256(file).digest():
        print("File integrity verified")         
        writeFile(file)
    else:
        print("File integrity compromised")


def handleInput():
    while True:
        global endConnection
        if endConnection:
            return

        data = recv_exact(s, 1)

        if data:

            if int(data[0]) == c.SEND_FILE_START:
                handleSendFile()
            elif int(data[0]) == c.SEND_CHAT:
                chat_message = s.recv(BUFFER_SIZE).decode('utf-8')
                print("")
                print("Chat message received: " + chat_message)
            elif int(data[0]) == c.ERROR_FILE_NOT_FOUND:
                print("Error: File not found on server")

            print("Enter a command: ")



def handleOutput():
    global targetFile
    while True:
        command = input("Enter a command: ")

        command = command.split()
        command[0] = command[0].lower()

        message = ''

        if command[0] == "leave":
            message = str(c.LEAVE)
        elif command[0] == "file":
            if command.__len__() < 2:
                message = str(c.REQUEST_FILE) + " " + targetFile
            else:
                message = str(c.REQUEST_FILE) + " " + command[1]
                targetFile = command[1]
        elif command[0] == "chat":
            newCommand = [str(x) for x in command[1:]]
            message = str(c.SEND_CHAT) + " " + ' '.join(newCommand)

        if message != '':
            s.send(message.encode('utf-8'))
            if command[0] == 'leave':
                print("Closing connection.")
                global endConnection
                endConnection = True
                return

thread1 = threading.Thread(target=handleInput)
thread2 = threading.Thread(target=handleOutput)

# Start the threads
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()

print("Connection closed.")

s.close()
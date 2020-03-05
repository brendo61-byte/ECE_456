from threading import Thread
from queue import Queue
import socket
import struct
import os

HOST = '127.0.0.1'
PORT = 5005
PACKET_SIZE = 1024
SUCCESS = b'File Has Been Transferred'
SAVEPATH = "server_data"


def writeFile(payload, fileName):
    with open(file=fileName, mode="w+b") as dataFile:
        dataFile.write(payload)


def checkSaveDir():
    if not os.path.isdir(SAVEPATH):
        command = f"mkdir {SAVEPATH}"
        os.system(command)


def pipeHandler(pipe):
    checkSaveDir()
    while True:
        while not pipe.empty():
            message = pipe.get()
            print("\n\nA new payload has arrived ...")
            print("Client suggests naming of this file as:\n'{}'".format(message["name"]))
            fileName = input('\nEnter "ok" to use the suggested name\nOtherwise enter the name you wish to save the file as\n(leave blank to not save)\n')

            if fileName:
                if fileName == "ok":
                    fileName = message["name"]
                    print("Using client suggested name")

                else:
                    print(f"Saving file as: {fileName}")

                print("\nSaving file ...")
                try:
                    saveFile(fileName=fileName, payload=message["payload"])
                    print("File has been saved ... ")
                except Exception as e:
                    print(f"Failed to save file\nError {e}")

            else:
                print("User has elected to not save this file...")

            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")


def saveFile(fileName, payload):
    filePath = os.path.join(SAVEPATH, fileName)
    with open(file=filePath, mode="w+b") as dataFile:
        dataFile.write(payload)


def main(pipe):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, PORT))
            sock.listen()
            conn, addr = sock.accept()

            count = 1
            first = True

            payload = b''

            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)

                    if first:
                        first = False

                        numOfPackets = struct.unpack('I', data[0:4])[0]
                        lengthOfName = struct.unpack('I', data[4:8])[0]
                        name = data[8:8 + lengthOfName].decode("utf-8")
                        data = data[8 + lengthOfName:]

                    if not data:
                        break

                    count += 1
                    payload += data

                    if count == numOfPackets:
                        print("Entire contents of file have been received")
                        conn.sendall(SUCCESS)
                        break

            message = {"payload": payload, "name": name}
            pipe.put(message)


if __name__ == '__main__':
    os.system("clear")
    pipe = Queue(maxsize=0)

    socketServer = Thread(target=main, args=(pipe,))
    userInput = Thread(target=pipeHandler, args=(pipe,))

    socketServer.start()
    userInput.start()

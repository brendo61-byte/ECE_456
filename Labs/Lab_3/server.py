import socket
import datetime
from DES import *

UDP_IP_SERVER_LOCAL = "127.0.0.1"
UDP_PORT = 5005
MAX_MESSAGE_SIZE = 5


def main(keyFile):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP_SERVER_LOCAL, UDP_PORT))

    key = getKeys(keyFile=keyFile)
    keyRev = reverseKey(key=key)

    messageList = []

    while True:
        data, addr = sock.recvfrom(2048)  # buffer size is 1024 bytes

        dataDecoded = DES(keySet=keyRev, data=data).decode("utf-8")

        if ord(dataDecoded[-1]) == 0:
            dataDecoded = dataDecoded[0:-1]

        if len(messageList) >= MAX_MESSAGE_SIZE:
            del messageList[0]

        receiverIPAddr = addr[0]
        receiverPort = addr[1]

        timeStamp = datetime.datetime.utcnow().strftime("%d/%m/%Y-%H:%M:%S")

        save = "Message: {}\nSender IP Address: {}\nTimeStamp (UTC): {}".format(dataDecoded, receiverIPAddr, timeStamp)

        messageList.append(save)

        encoded = DES(keySet=key, data=bytes(str(messageList), "utf-8"))

        sock.sendto(encoded, (receiverIPAddr, receiverPort))


if __name__ == '__main__':
    config = {
        "keyFile": "keyFileOne"
    }

    main(**config)

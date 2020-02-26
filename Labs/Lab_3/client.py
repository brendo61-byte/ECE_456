from DES import *
import timeout_decorator
import socket
import ast
import traceback

UDP_IP_Server = "127.0.0.1"
UDP_LOCAL_ADDR = "127.0.0.1"
UDP_PORT_SERVER = 5005

UDP_PORT = 5006
TIME_OUT = 5


class TimeOutError(BaseException):
    pass


def run(messageFile, keyFile):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_LOCAL_ADDR, UDP_PORT))

        message = getPayload(fileName=messageFile)

        if len(message) > 250:
            print("Max file size is 250 bytes. Program now exiting.")
            exit()

        key = getKeys(keyFile=keyFile)
        keyRev = reverseKey(key=key)

        encryptedData = DES(keySet=key, data=message)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t = sock.sendto(encryptedData, (UDP_IP_Server, UDP_PORT_SERVER))

        dataTemp = post(sock=sock)
        data = DES(keySet=keyRev, data=dataTemp)

        if data:
            tempData = data.decode("utf-8")
            if ord(tempData[-1]) == 0:
                tempData = tempData[0:-1]

            trueData = ast.literal_eval(tempData)

            messages = ""

            x = len(trueData)
            if x > 5:
                print("Data Length Wrong. Program Now exiting")
                exit()

            for entry in trueData:
                messages = ("\n{})\n{}".format(x, entry)) + messages
                x -= 1

            print(messages)

    except Exception as e:
        print("Something as comprised the socket connecting or data.\nError: {}\nTraceBack: {}".format(e, traceback.format_exc()))


@timeout_decorator.timeout(seconds=TIME_OUT, timeout_exception=TimeOutError)
def post(sock):
    try:
        while True:
            data, addr = sock.recvfrom(2048)  # buffer size is 1024 bytes
            return data
    except TimeOutError:
        print("Time Out Error. Could not get response from server. Program now exiting.")
        exit()


def main(config):
    run(**config)


if __name__ == '__main__':
    config = {
        "messageFile": "messageFileOne",
        "keyFile": "keyFileOne"
    }

    main(config=config)

import os
import socket
import struct
import sys
import traceback as tb

TIME_OUT = 10
PACK_VAL = 'Q'
MAX_PACK_SIZE = 2 ** 64 - 1
SEND_SIZE = 1024

"""
Client for Lab 5 using TCP connection. Inputs are command line args. Defaulted to working on a local machine via port 7500 if no
command line args are set.
"""


def getHostByName(nameOfServer):
    # gets IP address of server via hostname
    try:
        serverIP = socket.gethostbyname(nameOfServer)
        return serverIP

    except Exception as e:
        print("Unable to get IP address of host. Please check Server status, and ensure server port is open. Is server on the same network?"
              "\nError Out... \n\nException:\n{}\nTraceBack:\n{}".format(e, tb.format_exc()))

        programExit()


def run(nameOfServer, port, executionCount, timeDelay, command):
    # main call that runs everything
    serverIP = getHostByName(nameOfServer=nameOfServer)
    print(f"IP Address of Server: {serverIP}")

    call(serverIP=serverIP, port=port, executionCount=executionCount, timeDelay=timeDelay, command=command)


def call(serverIP, port, executionCount, timeDelay, command):
    # function formats data, sends message to server and waits for reply
    print(f"\nAttempting to connect to server @ {serverIP}:{port}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIME_OUT)

            sock.settimeout(TIME_OUT)
            sock.connect((serverIP, port))

            print("\nConnected to server ...")

            print(f"\nCommand For Server to run: {command}")
            print(f"Number of times command will run: {executionCount}")
            print(f"Delay between commands: {timeDelay}")

            payloadRaw = {
                "bytesEecutionCount": str(executionCount).encode("utf-8"),
                "bytesTimeDelay": str(timeDelay).encode('utf-8'),
                "bytesCommand": command.encode('utf-8')
            }

            print("\nGenerating Header ...")
            header = getHeader(payloadRaw=payloadRaw)

            print("\nGenerating Payload")
            payload = getPayload(payloadRaw=payloadRaw)

            print("\nFormatting Data ...")
            preFullMessage = header + payload
            pcksToSend = getNumberOfPacketsToSend(preFullMessage=preFullMessage)
            fullMessage = pcksToSend + preFullMessage

            print(f"Full Message: {fullMessage}")
            print("Length of message: {}".format(len(fullMessage)))

            print("\nSending Message...")
            sock.send(fullMessage)
            print("Message Sent")

            print("\nWaiting For Reply ...")

            receivedPayload = b''
            first = True

            while True:
                data = sock.recv(SEND_SIZE)

                if first:
                    print("Server is replying")
                    first = False
                    header = data[0:10]
                    payload = data[10:]

                    unpackedHeader = unpackHeader(header=header)
                    print("Expecting {} bytes of data from server".format(unpackedHeader))

                else:
                    payload = data

                receivedPayload += payload

                if len(receivedPayload) == unpackedHeader:
                    print("Message from server fully received")
                    unpackPayload(payload=receivedPayload)
                    break


    except ConnectionRefusedError as e:
        print("Unable to get connect to Server. Please check Server status, and ensure server port is open. Is server on the same network?"
              "\nError Out... \n\nException:\n{}\nTraceBack:\n{}".format(e, tb.format_exc()))

        programExit()


def unpackPayload(payload):
    print("Message From server reads:")
    decodedPayload = payload.decode("utf-8")
    print(decodedPayload)


def unpackHeader(header):
    toStr = header.decode("utf-8")
    temp = ''

    for char in toStr:
        temp = char + temp

    return int(temp)


def getNumberOfPacketsToSend(preFullMessage):
    size = len(preFullMessage) + 8

    numPackets = (size // SEND_SIZE)
    if (size / SEND_SIZE) > numPackets:
        numPackets += 1

    if numPackets > MAX_PACK_SIZE:
        print(f"Message is too large to send. Max number of packets to be sent to deliver message is {MAX_PACK_SIZE}")
        programExit()

    print(f"\nWill require {numPackets} packets to send all content")

    return struct.pack(PACK_VAL, numPackets)


def getPayload(payloadRaw):
    # formats data as a bytes string of ASCII
    payload = b''

    for val in payloadRaw.values():
        payload = payload + val

    print(f"Payload: {payload}")

    return payload


def getHeader(payloadRaw):
    # creates a header to tell server size of each argument
    # i.e. the command is 87 bytes long

    for key, val in payloadRaw.items():
        if len(val) > MAX_PACK_SIZE:
            print(f"{key} is too big. Max length is {MAX_PACK_SIZE}")
            print(programExit())

    header = b''

    for val in payloadRaw.values():
        temp = struct.pack(PACK_VAL, len(val))
        header = header + temp

    print(f"Header value: {header}")

    return header


def programExit():
    # so I don't have to keep re-writing these two lines
    print("\nProgram now exiting...")
    exit()


def checkInputs(inputArgs):
    # Checks to make sure that input args are as expected

    print("Input Args ...")
    for key, val in inputArgs.items():
        print(f"{key}: {val}")

    print()
    # check nameOfServer
    nameOfServer = inputArgs.get("nameOfServer")

    if nameOfServer is None:
        print("Please enter the hostname of the server")
        programExit()

    if type(nameOfServer) is not str:
        print("Servername must be of type string")
        programExit()

    # check port
    port = inputArgs.get("port")

    if port is None:
        print("Please enter a port number")

    if type(port) is not int:
        print("Port must be of type int")
        programExit()

    # check executionCount
    executionCount = inputArgs.get("executionCount")

    if executionCount is None:
        print("Please enter a executionCount number")

    if type(port) is not int:
        print("executionCount must be of type int")
        programExit()

    # checkTimeDelay
    executionCount = inputArgs.get("executionCount")

    if executionCount is None:
        print("Please enter a timeDelay number (in seconds)")

    if type(executionCount) is not int or type(executionCount) is not float:
        print("timeDelay must be of type int or float")
        programExit()

    # check command
    command = inputArgs.get("command")

    if command is None:
        print("Please enter a command")
        programExit()

    if type(nameOfServer) is not str:
        print("command must be of type string")
        programExit()

    print("\nAll inputs appear to be correct...\n")

def getCommands():
    i = 5
    temp = ""

    while True:
        try:
            temp += sys.argv[i] + " "
            i += 1
        except:
            return temp[:-1]

if __name__ == '__main__':
    os.system("clear")
    print("TCP Client Started...\n")
    try:
        inputArgs = {
            "nameOfServer": sys.argv[1],
            "port": int(sys.argv[2]),
            "executionCount": int(sys.argv[3]),
            "timeDelay": float(sys.argv[4]),
            "command": getCommands()
        }
    except Exception as e:
        print("Could not take command line args")
        print("Exception: {}\nTraceBack".format(e, tb.format_exc()))
        print("\nProgram now exiting")
        exit()

    run(**inputArgs)

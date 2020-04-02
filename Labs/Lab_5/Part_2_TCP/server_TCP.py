import os
import sys
import subprocess
import socket
import struct
import time
import traceback
import datetime

SIZE = 1024
PACK_VAL = 'Q'
PACK_SIZE = 8

OUTPUT_FILE = "system_call_output.txt"


def getLocalIPAdder():
    hostname = socket.gethostname()
    hostIP = socket.gethostbyname(hostname)
    return hostIP


def run(port):
    IP = getLocalIPAdder()
    listen(serverPort=port, IP=IP)


def listen(serverPort, IP):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((IP, serverPort))
        while True:
            sock.listen()

            conn, addr = sock.accept()

            first = True
            count = 0
            payload = b''

            with conn:
                if first:
                    print("\nNew connection")
                    print("Source IP: {}:{}".format(addr[0], addr[1]))
                    connectionStartTime = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    print("Current time: " + connectionStartTime)
                    print("Status=connected")

                data = conn.recv(1024)
                count += 1

                if first:
                    headerRaw = data[0:32]
                    payloadRaw = data[32:]
                    header, packetNum = unpackHeader(headerRaw=headerRaw)
                    first = False

                else:
                    payloadRaw = data

                payload += payloadRaw

                if count == packetNum:
                    print("\nAll packets received ...")
                    print(f"Byte val of Payload: {payload}")

                    unpackedPayload = unpackPayload(payload=payload, headers=header)
                    preRunArgs(unpackedPayload)

                    print("\nGenerating return payload...")

                    returnPayload = getReturnPayload(connectionStartTime=connectionStartTime)
                    conn.send(returnPayload)

                    print("Return Payload sent")


            print("\nConnection to client ended ...")
            print("Source IP: {}:{}".format(addr[0], addr[1]))
            connectionStartTime = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            print("Current time: " + connectionStartTime)
            print("Status=closed")
            print("Waiting for next client ...")


def getReturnPayload(connectionStartTime):
    # gets txt file into and creates length header
    outputTextRaw = "\nConnection Start Time: {} {}".format(connectionStartTime,  readArgOutput())

    payload = outputTextRaw.encode("utf-8")

    lenthOfPayload = len(payload)

    strOfLength = str(lenthOfPayload)
    padding = 10 - len(strOfLength)

    # bytesOfLength = strOfLength.encode("utf-8")

    bytesOfLength = b''
    tempPadding = b''
    zero = "0".encode("utf")

    for char in strOfLength:
        bytesOfLength = char.encode("utf-8") + bytesOfLength

    for i in range(padding):
        tempPadding += zero

    bytesOfLength = bytesOfLength + tempPadding

    return bytesOfLength + payload


def preRunArgs(unpackedPayload):
    # set up so system can run command
    print("\nSetting up for command execution...")

    clearOutputFile()

    unformatedCommand = unpackedPayload.get("command")
    commandArgs = formatCommand(unformatedCommand=unformatedCommand)

    print(f"Final command: {commandArgs}")

    executionCount = int(unpackedPayload.get("executionCount"))
    delay = float(unpackedPayload.get("timeDelay"))

    print("\nExecuting Command ...")
    for i in range(executionCount):
        runCommand(commandArgs=commandArgs, i=i, executionCount=executionCount)
        time.sleep(delay)

    print("Command Execution Complete")


def clearOutputFile():
    print("Cleaning Files")
    if os.path.isfile(OUTPUT_FILE):
        os.system(f"rm {OUTPUT_FILE}")

    os.system(f"touch {OUTPUT_FILE}")


def formatCommand(unformatedCommand):
    # reformat the command so that each arg is an entry in a list
    print("Reformatting command")
    temp = unformatedCommand

    return temp.split(" ")


def runCommand(commandArgs, i, executionCount):
    startTime = time.time()
    out = subprocess.Popen(commandArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    timeDelta = time.time() - startTime

    stdout, stderr = out.communicate()

    writeArgOutput(output=stdout.decode("utf-8"), i=i, timeDelta=timeDelta, executionCount=executionCount)


def writeArgOutput(output, i, timeDelta, executionCount):
    with open(OUTPUT_FILE, "a+") as textFile:
        textFile.write("\nCommand Iteration Number: {} of {}".format(i + 1, executionCount))
        textFile.write("\nTime to Preform Command: {0:.4f}".format(timeDelta))
        textFile.write("\nOutput:\n")
        textFile.write(output)


def readArgOutput():
    with open(OUTPUT_FILE, "r") as textFile:
        return textFile.read()


def unpackHeader(headerRaw):
    # unpacks the header of the message being sent
    print("\nUnpacking header ...")

    header = {
        "packetSize": None,
        "executionCountSize": None,
        "timeDelaySize": None,
        "commandSize": None
    }

    start = 0
    end = PACK_SIZE

    for key in header.keys():
        unPackVal = headerRaw[start:end]
        val = struct.unpack(PACK_VAL, unPackVal)
        header[key] = val[0]

        start += PACK_SIZE
        end += PACK_SIZE

    print("Header unpacked")

    for key, val in header.items():
        print(f"{key}: {val}")

    packetNum = header.get("packetSize")
    del header["packetSize"]

    return header, packetNum


def unpackPayload(payload, headers):
    # using the unpacked headers this will find the values for executionCount, timeDelay, and the command
    print("\nUnpacking Payload ...")

    payloadFormatted = {
        "executionCount": None,
        "timeDelay": None,
        "command": None
    }

    end = 0

    for sizeVal, key in zip(headers.values(), payloadFormatted.keys()):
        start = end
        end += sizeVal

        temp = payload[start:end]

        payloadFormatted[key] = temp.decode("utf-8")

    print("Payload unpacked")
    for key, val in payloadFormatted.items():
        print(f"{key}: {val}")

    return payloadFormatted


if __name__ == '__main__':
    os.system("clear")
    print("TCP Server Running ...")
    try:
        port = int(sys.argv[1])
    except Exception as e:
        print("Could not take command line arg for port")
        print("Exception: {}\nTraceBack".format(e, traceback.format_exc()))
        print("\nProgram now exiting")
        exit()

    print(f"Using port {port}")

    run(port=port)

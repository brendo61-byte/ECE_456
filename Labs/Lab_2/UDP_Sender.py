from struct import *

import sys
import traceback

KEYS = "Keys"
KEY_SIZE = 8

ZERO_PADDING = 0


def getKeys():
    try:
        with open(file=KEYS, mode="r+b") as payload:
            keys = payload.read()
            if len(keys) == KEY_SIZE:
                return keys
            else:
                print("Key Size is wrong")
    except FileNotFoundError:
        print("No keys file")
        exit()


def DES(keySet, data):
    global ZERO_PADDING

    if (len(data) % 2) is 1:
        data += bytes([0])
        ZERO_PADDING += 1

    newData = b''

    index = 0
    for i in range(2, len(data) + 2, 2):
        first, second = ord(data[index:i - 1]), ord(data[index + 1:i])

        for key in keySet:
            tempL = key ^ first
            tempR = key ^ second

            first = tempR
            second = tempL

        index += 2
        newData += bytes([first, second])

    return newData


def getInputArgs():
    try:
        dataFileName = sys.argv[1]
        sourceIPAddr = sys.argv[2]
        destinationIPAddr = sys.argv[3]
        sourcePort = sys.argv[4]
        destinationPort = sys.argv[5]
        outputFile = sys.argv[6]

        args = {
            "dataFileName": dataFileName,
            "sourceIPAddr": sourceIPAddr,
            "destinationIPAddr": destinationIPAddr,
            "sourcePort": sourcePort,
            "destinationPort": destinationPort,
            "outputFile": outputFile

        }

        return args

    except TypeError:
        print("Type Error: One or more input arguments are missing. Program now exiting.")
        exit()

    except Exception as e:
        print("An error has cased the program to crash. Now exiting.\nException: {}\n TraceBack: {}".format(e, traceback.format_exc()))
        exit()


def ipAddrToByes(address):
    ipOctetList = address.split('.')

    if len(ipOctetList) != 4:
        print("Invalid IP Address. Program now exiting")
        exit()

    ipHex = b''

    for octet in ipOctetList:
        val = int(octet)
        if val > 255:
            print("Invalid IP address. Program now exiting")
            exit()

        hexRep = pack('h', val)[0:1]

        ipHex = hexRep + ipHex

    return ipHex


def getData(filePath):
    try:
        with open(filePath, 'rb') as dataFile:
            data = dataFile.read()
            return data
    except FileNotFoundError:
        print("File Not Found: Please Provide a valid file. Program now exiting.")
        exit()


    except Exception as e:
        print("An error has cased the program to crash. Now exiting.\nException: {}\n TraceBack: {}".format(e, traceback.format_exc()))
        exit()


def writeEncryptedData(file, path):
    with open(file=path + '.bin', mode="w+b") as dataFile:
        dataFile.write(file)


def getPortByes(source, destination):
    global ZERO_PADDING

    if int(source) >= 2 ** 16 - 1:
        print("Invalid source port. Program now exiting")
        exit()

    if int(destination) >= 2 ** 16 - 1:
        print("Invalid destination port. Program now exiting")
        exit()

    sPort0, sPort1 = pack('H', int(source))[0:1], pack('H', int(source))[2:3]
    dPort0, dPort1 = pack('H', int(destination))[0:1], pack('H', int(destination))[2:3]

    if len(sPort1) == 0:
        sPort1 = bytes(1)
        ZERO_PADDING += 1

    if len(dPort1) == 0:
        dPort1 = bytes(1)
        ZERO_PADDING += 1

    sPort = sPort1 + sPort0
    dPort = dPort1 + dPort0

    return sPort, dPort


def send():
    global ZERO_PADDING
    inputArgs = getInputArgs()

    sourceIP = ipAddrToByes(address=inputArgs["sourceIPAddr"])
    destinationIP = ipAddrToByes(address=inputArgs["destinationIPAddr"])
    data = getData(filePath=inputArgs["dataFileName"])
    sourcePort, destinationPort = getPortByes(source=inputArgs["sourcePort"], destination=inputArgs["destinationPort"])

    # zeros = bytes(8)
    protocol = b'\x11'

    dataLength = len(data)
    print(dataLength)
    headerLength = 64 - ZERO_PADDING + dataLength
    print(headerLength)

    rawLength = dataLength + headerLength


    if rawLength >= 2 ** 16 - 1:
        print("Data too large to fit in one UDP packet. Program now exiting")
        exit()

    totalLength0 = pack('H', rawLength)[0:1]
    totalLength1 = pack('H', rawLength)[2:3]

    if len(totalLength1) == 0:
        totalLength1 = bytes(1)

    totalLength = totalLength1 + totalLength0

    checkSum = int.from_bytes(sourceIP, byteorder='big') + int.from_bytes(destinationIP, byteorder='big') + int.from_bytes(protocol, byteorder='big') + int.from_bytes(totalLength,
                                                                                                                                                                       byteorder='big') + int.from_bytes(
        sourcePort, byteorder='big') + int.from_bytes(destinationPort, byteorder='big') + int.from_bytes(totalLength, byteorder='big')


    while checkSum >= 2 ** 16:
        checkSum -= (2 ** 16)
        checkSum += 1

    checkSum = (2 ** 16) - checkSum
    print(checkSum)
    x = pack('H', checkSum)

    l = []
    for byte in x:
        temp = bytes([byte])
        l.append(temp)

    checkSum = l[1] + l[0]

    final = sourcePort + destinationPort + totalLength + checkSum + data

    print("\nData Encoded using big-endian format")
    print("               Source IP Address: {}".format(sourceIP))
    print("          Destination IP Address: {}".format(destinationIP))

    val = 1
    for byte in sourceIP:
        print("                 Source IP Byte{}: {}".format(val, byte))
        val += 1
    val = 1
    for byte in destinationIP:
        print("            Destination IP Byte{}: {}".format(val, byte))
        val += 1

    print("  File Size (bytes - no zero padding): {}".format(rawLength - ZERO_PADDING))
    print("                         Total Length: {}".format(rawLength))
    print("                      Check Sum (hex): {}".format(checkSum.hex()))


    keys = getKeys()
    encryptedData = DES(keySet=keys, data=final)
    writeEncryptedData(file=encryptedData, path=inputArgs["outputFile"])
    print("...Data has been encrypted and saved.")
    print(final)
    print(int.from_bytes(checkSum, byteorder='big'))
    print()


if __name__ == '__main__':
    send()

from struct import *
import sys
import traceback

KEYS = "Keys"
KEY_SIZE = 8


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


def reverseKey(key):
    revKey = b''
    for i in key:
        revKey = bytes([i]) + revKey

    return revKey


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


def getInputArgs():
    try:
        sourceIPAddr = sys.argv[1]
        destinationIPAddr = sys.argv[2]
        inputFile = sys.argv[3]

        args = {
            "sourceIPAddr": sourceIPAddr,
            "destinationIPAddr": destinationIPAddr,
            "inputFile": inputFile

        }

        return args

    except TypeError:
        print("Type Error: One or more input arguments are missing. Program now exiting.")
        exit()

    except Exception as e:
        print("An error has cased the program to crash. Now exiting.\nException: {}\n TraceBack: {}".format(e, traceback.format_exc()))
        exit()


def readEncryptedData(file):
    try:
        with open(file=file + '.bin', mode="r+b") as dataFile:
            info = dataFile.read()
            return info

    except FileNotFoundError:
        print("No file containing encrypted message")
        exit()


def writeDecryptedFile(file, path):
    with open(file=path, mode="w+b") as dataFile:
        dataFile.write(file)


def DES(keySet, data):
    newData = b''

    if (len(data) % 2) is 1:
        data += bytes([0])

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


def receive():
    inputArgs = getInputArgs()
    sourceIP = ipAddrToByes(address=inputArgs["sourceIPAddr"])
    destinationIP = ipAddrToByes(address=inputArgs["destinationIPAddr"])
    encryptedData = readEncryptedData(file=inputArgs["inputFile"])
    keys = getKeys()
    keys = reverseKey(key=keys)
    protocol = b'\x11'
    data = DES(keySet=keys, data=encryptedData)

    if data[-1] == 0:
        data = data[:-1]

    info = []
    for byte in data:
        info.append(bytes([byte]))

    sourcePort = info[0] + info[1]
    destinationPort = info[2] + info[3]
    totalLength = info[4] + info[5]
    checkSumFrom = info[6] + info[7]

    data = b''
    for i in range(8, len(info)):
        data += info[i]

    checkSum = int.from_bytes(sourceIP, byteorder='big') + int.from_bytes(destinationIP, byteorder='big') + int.from_bytes(protocol, byteorder='big') + int.from_bytes(totalLength,
                                                                                                                                                                       byteorder='big') + int.from_bytes(
        sourcePort, byteorder='big') + int.from_bytes(destinationPort, byteorder='big') + int.from_bytes(totalLength, byteorder='big')

    while checkSum >= 2 ** 16:
        checkSum -= (2 ** 16)
        checkSum += 1

    print(checkSum)
    print(checkSumFrom.hex())
    x = pack('H', checkSum)

    l = []
    for byte in x:
        temp = bytes([byte])
        l.append(temp)

    checkSum = l[1] + l[0]

    print()
    print(int.from_bytes(checkSum, byteorder='big'))

    sumTotal = int.from_bytes(checkSum, byteorder='big') + int.from_bytes(checkSumFrom, byteorder='big')

    print(sumTotal)

    if sumTotal > 65535 + 1:
        print("\nCheck sums did not add up.")
        print("Data has been comprised. Program now exiting")
        exit()

    x2 = pack('H', sumTotal - 1)

    l = []
    for byte in x2:
        temp = bytes([byte])
        l.append(temp)

    checkSumNew = l[1] + l[0]

    print("     Source Port Address: {}".format(sourceIP.hex()))
    print("Destination Port Address: {}".format(destinationIP.hex()))

    print("            Total Length: {}".format(int.from_bytes(totalLength, byteorder='big')))
    print("         Check Sum (hex): {}".format(checkSumNew.hex()))

    print(checkSumNew)

    if checkSumNew == b'\xff\xff':
        print("\nCheck sum successful")

        writeDecryptedFile(file=data, path='output')
        print("...Data Has Been Saved")

    else:
        print("\nCheck sums did not add up.")
        print("Data has been comprised. Program now exiting")
        exit()


if __name__ == '__main__':
    receive()

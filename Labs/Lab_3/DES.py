KEYS = "Keys"
PAYLOAD = "check"
ENCRYPTED = "encrypted"
DECRYPTED = "decrypted"

KEY_SIZE = 8


def getKeys(keyFile):
    try:
        with open(file=keyFile, mode="r+b") as payload:
            keys = payload.read()
            if len(keys) == KEY_SIZE:
                return keys
            else:
                print("Key Size is wrong")
    except FileNotFoundError:
        print("No keys file")


def reverseKey(key):
    revKey = b''
    for i in key:
        revKey = bytes([i]) + revKey

    return revKey


def getPayload(fileName):
    try:
        with open(file=fileName, mode="r+b") as readFile:
            payload = readFile.read()
            if len(payload) == 0:
                print("That is a blank file. Nice Try Emily.")
                exit()

            return payload

    except FileNotFoundError:
        print("No payload file")
        exit()


def DES(keySet, data):
    if (len(data) % 2) is 1:
        data += bytes([0])

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

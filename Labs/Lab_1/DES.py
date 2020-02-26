KEYS = "Keys"
PAYLOAD = "check"
ENCRYPTED = "encrypted"
DECRYPTED = "decrypted"

KEY_SIZE = 8


def getKeys(keyFile):
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


def writeEncryptedData(file):
    with open(file=ENCRYPTED, mode="w+b") as dataFile:
        dataFile.write(file)


def readEncryptedData():
    try:
        with open(file=ENCRYPTED, mode="r+b") as dataFile:
            info = dataFile.read()
            return info

    except FileNotFoundError:
        print("No file containing encrypted message")
        exit()


def writeDecryptedFile(file):
    with open(file=DECRYPTED, mode="w+b") as dataFile:
        dataFile.write(file)


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


def encrypt():
    keys = getKeys()
    payload = getPayload()
    encryptedData = DES(keySet=keys, data=payload)
    writeEncryptedData(file=encryptedData)


def decrypt():
    keysOrdered = getKeys()
    keys = reverseKey(key=keysOrdered)
    payload = readEncryptedData()
    decryptedData = DES(keySet=keys, data=payload)

    if decryptedData[-1] == 0:
        decryptedData = decryptedData[0:-1]

    writeDecryptedFile(file=decryptedData)


if __name__ == '__main__':
    encrypt()
    decrypt()

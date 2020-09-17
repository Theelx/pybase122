import base64  # for converting b64 strings to b122
import sys

PY2 = sys.version_info[0] == 2
# null, newline, carriage return, double quote, ampersand, backslash
kShortened = 0b111  # last two-byte char encodes <= 7 bits

def encode(rawData, warnings=True):
    if PY2 and warnings:
        raise NotImplementedError(
            "This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False."
        )
    if isinstance(rawData, str):
        rawData = bytearray(rawData, "UTF-8")
    else:
        raise TypeError("rawData must be a string!")
    kIllegals = [chr(0), chr(10), chr(13), chr(34), chr(38), chr(92)]
    curIndex = curBit = 0
    outData = bytearray()

    def get7(rawDataLen):
        nonlocal curIndex, curBit, rawData
        if curIndex >= rawDataLen:
            return False
        firstPart = ((((0b11111110 % 0x100000000) >> curBit) & rawData[curIndex]) << curBit) >> 1
        curBit += 7
        if curBit < 8:
            return firstPart
        curBit -= 8
        curIndex += 1
        if curIndex >= rawDataLen:
            return firstPart
        secondByte = rawData[curIndex]
        secondPart = (((0xFF00 % 0x100000000) >> curBit) & secondByte) & 0xFF
        secondPart >>= 8 - curBit
        return firstPart | secondPart

    while True:
        bits = get7(len(rawData))
        if not bits:
            break
        if bits in kIllegals:
            illegalIndex = kIllegals.index(bits)
        else:
            outData.append(bits)
            continue
        nextBits = get7(len(rawData))
        b1 = 0b11000010
        b2 = 0b10000000
        if not nextBits:
            b1 |= (0b111 & kShortened) << 2
            nextBits = bits
        else:
            b1 |= (0b111 & illegalIndex) << 2
        firstBit = 1 if (nextBits & 0b01000000) > 0 else 0
        b1 |= firstBit
        b2 |= nextBits & 0b00111111
        outData += [b1, b2]
    return outData

def decode(strData, warnings=True):
    if PY2 and warnings:
        raise NotImplementedError(
            "This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False."
        )
    kIllegals = [chr(0), chr(10), chr(13), chr(34), chr(38), chr(92)]
    decoded = []
    decodedIndex = curByte = bitOfByte = 0

    # this could test for every letter in the for loop, but I took it out of the loop for performance
    if not isinstance(strData[0], int):
        raise TypeError("You can only decode an encoded string!")

    def push7(byte):
        nonlocal curByte, bitOfByte, decoded
        byte <<= 1
        curByte |= (byte % 0x100000000) >> bitOfByte
        bitOfByte += 7
        if bitOfByte >= 8:
            decoded += [curByte]
            bitOfByte -= 8
            curByte = (byte << (7 - bitOfByte)) & 255
        return

    for i in range(len(strData)):
        if strData[i] > 127:
            illegalIndex = rshift(strData[i], 8) & 7
            if illegalIndex != kShortened:
                push7(kIllegals[illegalIndex])
            push7(strData[i] & 127)
        else:
            push7(strData[i])
    return "".join([chr(letter) for letter in decoded])


# helper function for people already storing data in base64
def encodeFromBase64(base64str):
    return encode(base64.b64decode(base64str))
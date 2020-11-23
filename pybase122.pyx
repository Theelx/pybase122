# distutils: language=c++
# cython: boundscheck=False, wraparound=False, cdivision=True
cimport cython
import sys
import time  # for performance timing
from libcpp.vector cimport vector

PY2 = sys.version_info[0] == 2

# null, newline, carriage return, double quote, ampersand, backslash
cdef int[6] illegalByteByIndex
illegalByteByIndex[0] = ord('\0')
illegalByteByIndex[1] = ord('\n')
illegalByteByIndex[2] = ord('\r')
illegalByteByIndex[3] = ord('"')
illegalByteByIndex[4] = ord('&')
illegalByteByIndex[5] = ord('\\')

cdef int[256] illegalIndexByByte
cdef int i

for i in range(256):
    illegalIndexByByte[i] = -1
for i in range(len(illegalByteByIndex)):
    illegalIndexByByte[illegalByteByIndex[i]] = i

cdef int rshift(long int val, long int n) nogil:
    if val >= 0:
        return val >> n
    else:
        return (val + <int>0x100000000) >> n

cdef (int, int, int) get7(int rawDataLen, int curIndex, int curBit, bytearray rawDataBytes) nogil:
    cdef int firstPart, secondPart

    if curIndex >= rawDataLen:
        return False, curIndex, curBit
    firstPart = (
        ((rshift(0b11111110, 0x100000000) >> curBit) & rawDataBytes[curIndex]) << curBit
    ) >> 1
    curBit += 7
    if curBit < 8:
        return firstPart, curIndex, curBit
    curBit -= 8
    curIndex += 1
    if curIndex >= rawDataLen:
        return firstPart, curIndex, curBit
    secondPart = (((rshift(0xFF00, 0x100000000) >> curBit) & rawDataBytes[curIndex]) & 0xFF) >> (8 - curBit)
    return (firstPart | secondPart), curIndex, curBit

cdef (int, int) push7(int byte, int curByte, int bitOfByte, vector[int]& decoded):
    byte <<= 1
    curByte |= rshift(byte, 0x100000000) >> bitOfByte
    bitOfByte += 7
    if bitOfByte >= 8:
        decoded.push_back(curByte)
        bitOfByte -= 8
        curByte = (byte << (7 - bitOfByte)) & 255
    return (curByte, bitOfByte)

cpdef bytearray encode(str rawData, bint warnings=True):
    cdef int curIndex, curBit, rawDataLen, illegalIndex, kShortened, b1, b2, bits, nextBits
    cdef bytearray firstPart
    cdef int firstBit
    #cdef list kIllegals
    cdef bytearray rawDataBytes
    outData = bytearray()

    if PY2 and warnings:
        raise NotImplementedError("This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False.")
    if isinstance(rawData, str):
        rawDataBytes = bytearray(rawData, "UTF-8")
    else:
        raise TypeError("rawData must be a string!")
    kShortened = 0b111  # last two-byte char encodes <= 7 bits
    curIndex = curBit = 0

    #    for loops don't work because they cut off a variable amount of end letters for some reason, but they'd speed it up immensely
    #    for i in range(len(rawDataBytes)):
    while True:
        bits, curIndex, curBit = get7(len(rawDataBytes), curIndex, curBit, rawDataBytes)
        if not bits:
            break
        illegalIndex = illegalIndexByByte[bits]
        if illegalIndex == -1:
            outData.append(bits)
            continue

        nextBits, curIndex, curBit = get7(len(rawDataBytes), curIndex, curBit, rawDataBytes)
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
        outData.append(b1)
        outData.append(b2)
    return outData

cpdef str decode(bytearray strData, bint warnings=True):
    cdef vector[int] decoded
    cdef int illegalIndex
    cdef int decodedIndex, curByte, bitOfByte, kShortened, int_strData

    if PY2 and warnings:
        raise NotImplementedError(
            "This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False."
        )
    kShortened = 0b111  # last two-byte char encodes <= 7 bits
    decodedIndex = curByte = bitOfByte = 0

    # this could test for every letter in the for loop, but I took it out for performance
    if not isinstance(strData[0], int):
        raise TypeError("You can only decode an encoded string!")

    cdef int i = 0
    while i < len(strData):
        int_strData = <int>(strData[i])
        i += 1
        if int_strData > 127:
            int_strData = (int_strData & 0b00011111) << 6 | (<int>(strData[i]) & 0b00111111)
            i += 1
            illegalIndex = (int_strData >> 8) & 7
            if illegalIndex != kShortened:
                curByte, bitOfByte = push7(illegalByteByIndex[illegalIndex], curByte, bitOfByte, decoded)
            curByte, bitOfByte = push7(int_strData & 127, curByte, bitOfByte, decoded)
        else:
            curByte, bitOfByte = push7(int_strData, curByte, bitOfByte, decoded)
    return "".join(map(chr, decoded))


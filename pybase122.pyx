# distutils: language=c++
cimport cython
from libc.stdlib cimport abort, malloc, free
import sys
import time  # for performance timing
from libcpp.string cimport string
from libcpp.list cimport list as cpplist
from libcpp.vector cimport vector

PY2 = sys.version_info[0] == 2

class SpeedException(Exception):
    pass

cdef int rshift(long int val, long int n) nogil:
    if val >= 0:
        return val >> n
    else:
        return (val + <int>0x100000000) >> n

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef (int, int, int) get7(int rawDataLen, int curIndex, int curBit, bytearray rawDataBytes):
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

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef tuple push7(int byte, int curByte, int bitOfByte, list decoded):
    byte <<= 1
    curByte |= rshift(byte, 0x100000000) >> bitOfByte
    bitOfByte += 7
    if bitOfByte >= 8:
        decoded.append(curByte)
        bitOfByte -= 8
        curByte = (byte << (7 - bitOfByte)) & 255
    return curByte, bitOfByte, decoded

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef bytearray encode(str rawData, bint warnings=True, bint speed=True):
    cdef int curIndex, curBit, rawDataLen, illegalIndex, kShortened, b1, b2, bits, nextBits
    cdef bytearray firstPart
    cdef int firstBit
    cdef cpplist[int] outData
    cdef bytearray rawDataBytes

    if PY2 and warnings:
        raise NotImplementedError("This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False.")
    if isinstance(rawData, str):
        rawDataBytes = bytearray(rawData, "UTF-8")
    else:
        raise TypeError("rawData must be a string!")
    # null, newline, carriage return, double quote, ampersand, backslash
    if speed:
        kIllegals = {chr(0), chr(10), chr(13), chr(34), chr(38), chr(92)}
    else:
        kIllegals = [chr(0), chr(10), chr(13), chr(34), chr(38), chr(92)]
    kShortened = 0b111  # last two-byte char encodes <= 7 bits
    curIndex = curBit = 0

    #    for loops don't work because they cut off a variable amount of end letters for some reason, but they'd speed it up immensely
    while True:
        bits, curIndex, curBit = get7(len(rawDataBytes), curIndex, curBit, rawDataBytes)
        #bits, curIndex, curBit = no[0], no[1], no[2]
        if not bits:
            break
        if bits in kIllegals:
            if speed:
                raise SpeedException("Encode is much faster without allowing illegal characters! Pass speed=False to disable this.")
            else:
                illegalIndex = kIllegals.index(bits)
        else:
            outData.push_back(bits)
            continue
        nextBits, curIndex, curBit = get7(len(rawDataBytes), curIndex, curBit, rawDataBytes)
        #nextBits, curIndex, curBit = no[0], no[1], no[2]
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
        outData.push_back(b1)
        outData.push_back(b2)
    return bytearray(outData)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef str decode(bytearray strData, bint warnings=True):
    cdef list kIllegals = [0, 10, 13, 34, 38, 92]
    cdef list decoded = []
    cdef bytes illegalIndex
    cdef int decodedIndex, curByte, bitOfByte, kShortened, int_strData

    if PY2 and warnings:
        raise NotImplementedError(
            "This hasn't been tested on Python2 yet! Turn this warning off by passing warnings=False."
        )
    # null, newline, carriage return, double quote, ampersand, backslash
    kShortened = 0b111  # last two-byte char encodes <= 7 bits
    decodedIndex = curByte = bitOfByte = 0

    # this could test for every letter in the for loop, but I took it out for performance
    if not isinstance(strData[0], int):
        raise TypeError("You can only decode an encoded string!")

    for i in range(len(strData)):
        int_strData = int(strData[i])
        if int_strData > 127:
            illegalIndex = (rshift(int_strData, 0x100000000) >> 8) & 7
            if illegalIndex != kShortened:
                curByte, bitOfByte, decoded = push7(chr(kIllegals[illegalIndex]), curByte, bitOfByte, decoded)
            curByte, bitOfByte, decoded = push7(int_strData & 127, curByte, bitOfByte, decoded)
        else:
            curByte, bitOfByte, decoded = push7(int_strData, curByte, bitOfByte, decoded)
    return "".join([chr(letter) for letter in decoded])

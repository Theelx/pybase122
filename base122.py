# null, newline, carriage return, double quote, ampersand, backslash
kIllegals = [chr(0), chr(10), chr(13), chr(34), chr(38), chr(92)]
kShortened = 0b111 # last two-byte char encodes <= 7 bits

def encode(rawData):
    if isinstance(rawData, str):
        rawData = bytearray(rawData, 'UTF-8')
    else:
        raise TypeError("rawData must be a string!")
    curIndex = curBit = 0
    curMask = b'0b10000000'
    outData = bytearray()

    def get7():
        nonlocal curIndex, curMask, rawData, curBit
        if curIndex >= len(rawData):
            return False
        firstByte = rawData[curIndex]
        firstPart = (((0b11111110 % 0x100000000) >> curBit) & firstByte) << curBit
        firstPart >>= 1
        curBit += 7
        if curBit < 8:
            return firstPart
        curBit -= 8
        curIndex += 1
        if curIndex >= len(rawData):
            return firstPart
        secondByte = rawData[curIndex]
        secondPart = (((0xFF00 % 0x100000000) >> curBit) & secondByte) & 0xFF
        secondPart >>= 8 - curBit
        return firstPart | secondPart

    while True:
        bits = get7()
        if not bits:
            break
        try:
            illegalIndex = kIllegals.index(bits)
        except ValueError:
            outData.append(bits)
            continue
        nextBits = get7()
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
        outData.extend([b1, b2])
    return outData

def decode(strData):
    decoded = []
    decodedIndex = curByte = bitOfByte = 0

    def push7(byte):
        nonlocal curByte, bitOfByte, decoded
        byte <<= 1
        curByte |= (byte % 0x100000000) >> bitOfByte
        bitOfByte += 7
        if bitOfByte >= 8:
            decoded.append(curByte)
            bitOfByte -= 8
            curByte = (byte << (7 - bitOfByte)) & 255

    for i in range(len(strData)):
        c = strData[i]
        if c > 127:
            illegalIndex = rshift(c, 8) & 7
            if illegalIndex != kShortened:
                push7(kIllegals[illegalIndex])
            push7(c & 127)
        else:
            push7(c)
    return ''.join([chr(letter) for letter in decoded])

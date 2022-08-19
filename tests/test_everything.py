import pyximport

pyximport.install()
from cybase122 import decode as cydecode
from cybase122 import encode as cyencode
from pybase122 import decode, encode, encode_from_base64

import random
def get_random_unicode(length):
    try:
        get_char = unichr
    except NameError:
        get_char = chr
    # Update this to include code point ranges to be sampled
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]
    alphabet = [
        get_char(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))

def test_pure_py_ascii_encode():
    example_str = "hello world!"
    assert encode(example_str) == bytearray(b"4\x19-Fc<@w7\\MF!\x04")


def test_pure_py_ascii_roundtrip():
    example_str = "hello world!"
    assert decode(encode(example_str)) == example_str


def test_pure_py_utf8_encode():
    example_str = "мир привет!"  # 'hello world!'
    assert encode(example_str) == bytearray(
        b"h/\x1a\x0bFF\x00 h/z\x18\x06BqPY4\x16]\x0c\x08B"
    )


def test_pure_py_utf8_roundtrip():
    example_str = "мир привет!"  # 'hello world!'
    assert decode(encode(example_str)) == example_str


def test_cython_ascii_encode():
    example_str = "hello world!"
    assert cyencode(example_str) == bytearray(b"4\x19-Fc<@w7\\MF!\x04")


def test_cython_ascii_roundtrip():
    example_str = "hello world!"
    assert cydecode(cyencode(example_str)) == example_str


def test_cython_utf8_encode():
    example_str = "мир привет!"  # 'hello world!'
    #print(chr(92), "|", chr(77), "|", ord('\\'))
    print(encode(example_str))
    assert cyencode(example_str) == bytearray(
        b"h/\x1a\x0bFF\x00 h/z\x18\x06BqPY4\x16]\x0c\x08B"
    )


def test_cython_utf8_roundtrip():
    with open('./tests/random_unicode.txt', 'r+') as f:
        example_str = f.read()
    assert cydecode(cyencode(example_str)) == example_str

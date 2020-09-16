# base122
This is a simple Python 3 implementation of the base122 binary-to-text encoding made for JS/HTML [here](https://github.com/kevinAlbs/Base122) by kevinAlbs.

# How To Use
base122.py contains an encode method and a decode method. It does not have the encode/decode file feature of kevinAlbs' version.
```py
from base122 import encode, decode

example_str = 'hello world!'
print(encode(example_str)) # bytearray(b'4\x19-Fc<@w7\\MF!\x04')
print(decode(encode(example_str)) # 'hello world!'
print(decode(example_str) # TypeError: You can only decode an encoded string!
```

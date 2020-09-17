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
Do not use anything from original_base122.py unless you're comparing, as that's the version I transliterated that stuck almost exactly to the original NodeJS version but in Python.
You should use the current base122.py, as that's quite a bit faster due to some optimizations I made for Python.

# Why I Did This
I learned to code Python (horribly) by playing with the internals of a friend's Discord bot, and it just so happened that they decided to store their data in a database with jsonpickle-encoded strings. While I migrated my fork of the bot to not use jsonpickle and make the db atomic, I have another friend who still uses jsonpickle on their fork, and their database is huge. I figured that by adapting base122 to Python, they'd switch over from using base64 encoding for the internal steps in jsonpickle to base122, because a potential switch to base85 wasn't that big of a deal for them (33% bloat to 25% for base85, compared to 14% for base122).
While my rationale for making this may end up being pointless if they stop using jsonpickle, it's still fun to adapt something new to Python that hasn't been done before. Plus, maybe it'll help someone stumbling upon this someday!

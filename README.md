# base122
This is a simple Python 3 implementation of the base122 binary-to-text encoding made for JS/HTML [here](https://github.com/kevinAlbs/Base122) by kevinAlbs. Base122 isn't 8-bit clean, so it can only be used on ascii characters.

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
You should use the current base122.py, as that's quite a bit faster due to some optimizations I made for Python, and original_base122.py has a subtle bug in its `get7` method.

# How to Build
To build the Cython version, run the following steps:
```bash
git clone https://github.com/Theelx/pybase122.git
cd pybase122
pip install -U --pre cython
python3 setup_cython.py build_ext --inplace
```
Once the last command is complete, you can put `import pybase122` into any of your scripts and run its functions much quicker!

Note: It is highly recommended for you to install Cython>=3.0.0a11, as the Cython 3.0 series is essentially stable, even though it is called "alpha". This repo has only been tested on Cython==3.0.0a11.

# Performance
The pybase122.pyx is much faster when compiled with Cython 3.0a6 vs the normal script. It runs about 6x faster than the other script on my test string of 10000 runs of 25 words/180 bytes of Lorem Ipsum text on a 3-core, 3.8GHz AMD Ryzen 9 3900X VPS. I first set the string as the text encoded/decoded with ascii, then ran decode(encode(TEST_STR)), and timed 10000 runs of that.

Results:
Tentatively, base64 > Cython 3.0a6 => base85 > Python 3.8.3. I haven't tested memory usage or CPU usage though, so this could be a flawed benchmark. In addition, one very interesting thing I noticed was that the base64 encoding/decoding speed stayed basically the same whether 180 bytes or 20, while base85 scaled between slightly slower than and about the same as Cython, and Python scaled quickly.

Desmos Graphs of Various Byte Input Sizes:  
https://www.desmos.com/calculator/oeqwthbpnb - encode()  
https://www.desmos.com/calculator/li4bs9nngf - encode(decode()) a.k.a. Total  
If someone wants to subtract the encoding from Total to make Decoding, feel free.  
**These benchmarks are using the scripts as they were on 6/10/2020 (dd/mm/yyyy)**

# Why I Did This
I learned to code Python (horribly) by playing with the internals of a friend's Discord bot, and it just so happened that they decided to store their data in a database with jsonpickle-encoded strings. While I migrated my fork of the bot to not use jsonpickle and make the db atomic, I have another friend who still uses jsonpickle on their fork, and their database is huge. I figured that by adapting base122 to Python, they'd switch over from using base64 encoding for the internal steps in jsonpickle to base122, because a potential switch to base85 wasn't that big of a deal for them (33% bloat to 25% for base85, compared to 14% for base122).
While my rationale for making this may end up being pointless if they stop using jsonpickle, it's still fun to adapt something new to Python that hasn't been done before. Plus, maybe it'll help someone stumbling upon this someday!

# Issues
Please state the Python version you're using, provide a description of the issue, and give the shortest/simplest example you can with the results.
Example:
"Hi, I'm using Python 3.9 and the text comes out garbled when I decode an encoded string:"
```py
from base122 import encode, decode

example_str = 'мир привет!' # 'hello world!'
print(encode(example_str)) # bytearray(b'h/\x1a\x0bFF')
print(decode(encode(example_str)) # Ð¼Ð¸Ñ
```

My response:
"Hello, base122 doesn't work with utf-8 strings because it isn't 8-bit clean. Please use only ascii with this. Thanks for trying it out though!"

# Contribute
All contributions are welcome! If you want to add something or speed something up*, feel free to submit a pull request, I'll try to check it as soon as I can!

*If you want to speed something up, please include timing for affected lines from line_profiler, which can be found [here](https://github.com/Theelx/line_profiler). If the new code significantly impacts readability or requires a new dependency, please include it as a new file.

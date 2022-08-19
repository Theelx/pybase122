import base64
import time

import cybase122
import pybase122

with open("./tests/random_unicode.txt", "r+") as f:
    example_str2 = f.read()

def run_benchmarks(encode_func, decode_func, use_bytes=False, title=""):
    if use_bytes:
        example_str = bytes(example_str2, 'utf-8')
    else:
        example_str = example_str2
    start_encode = time.perf_counter()
    result = encode_func(example_str)
    elapsed_encode_ms = round((time.perf_counter() - start_encode) * 1000, 2)

    start_decode = time.perf_counter()
    result2 = decode_func(result)
    elapsed_decode_ms = round((time.perf_counter() - start_decode) * 1000, 2)
    
    print(f"{title}\nEncode: {elapsed_encode_ms}ms\nDecode: {elapsed_decode_ms}ms\nResults Correct: {example_str == result2}\n")

funcs = [(base64.b64encode, base64.b64decode, True, "Base64:"), (base64.b85encode, base64.b85decode, True, "Base85:"), (pybase122.encode, pybase122.decode, False, "PyBase122:"), (cybase122.encode, cybase122.decode, False, "CyBase122:")]
for encode, decode, use_bytes, title in funcs:
    run_benchmarks(encode, decode, use_bytes, title)

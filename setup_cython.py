# cython: language_level=3
import os
import sys

from Cython.Build import cythonize
from setuptools import Extension, setup

os.environ["CFLAGS"] = "-march='native' -Wno-sign-compare -flto -pipe"

ext = Extension(name="cybase122", sources=["cybase122.pyx"])
setup(
    ext_modules=cythonize(
        ext,
        annotate=True,
        compiler_directives={
            "language_level": 3,
            "infer_types": True,
            "embedsignature": True,
        },
    )
)

#cython: language_level=3
from setuptools import Extension, setup
from Cython.Build import cythonize
import os
import sys

os.environ["CFLAGS"] = "-Wno-sign-compare -flto -pipe"

ext = Extension(name="pybase122", sources=["pybase122.pyx"])
setup(ext_modules=cythonize(ext, annotate=True, compiler_directives={'language_level': 3, "infer_types": True}))

import os

try:
    from Cython.Build import cythonize
except (ImportError, NameError):
    # skip cythonizing
    cythonize = lambda x: 0
from setuptools import Extension, setup

with open("README.md", "r+") as f:
    long_description = f.read()

setup(
    name="pybase122",
    version="0.1.0",
    description="pybase122: Encode and decode base122 data quickly and easily!",
    license="The Unlicense",
    url="https://github.com/Theelx/pybase122",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    scripts=["pybase122.py"],
    setup_requires=["Cython>=3.0.0a11"],
    python_requires=">=3.5",
    ext_modules=cythonize(
        Extension(
            "cybase122",
            ["cybase122.pyx"],
            language="c++",
            # consider including -march=native if it makes a speed difference
            # and if portability isn't a concern for users
            extra_compile_args=["-Wno-sign-compare", "-flto", "-pipe"],
            compiler_directives={"language_level": 3, "infer_types": True},
        )
    ),
)

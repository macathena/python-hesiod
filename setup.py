#!/usr/bin/python

from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    name="PyHesiod",
    version="0.2.12",
    description="PyHesiod - Python bindings for the Heisod naming library",
    author="Evan Broder",
    author_email="broder@mit.edu",
    maintainer="Debathena Project",
    maintainer_email="debathena@mit.edu",
    url="http://ebroder.net/code/PyHesiod",
    license="MIT",
    py_modules=['hesiod'],
    ext_modules=cythonize([
        Extension("_hesiod",
                  ["_hesiod.pyx"],
                  libraries=["hesiod"]),
    ]),
)

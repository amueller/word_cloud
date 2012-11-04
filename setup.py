
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'numcy',
    ext_modules = cythonize("*.pyx"),
)


from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='integral',
    ext_modules=cythonize("*.pyx"),
)

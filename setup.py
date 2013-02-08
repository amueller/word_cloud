
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='word_cloud',
    ext_modules=cythonize("*.pyx"),
    package_dir={'word_cloud': '.'}
)

from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("wordcloud/query_integral_image.pyx"))

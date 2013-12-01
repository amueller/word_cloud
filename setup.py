from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='wordcloud',
    ext_modules=cythonize('wordcloud/query_integral_image.pyx'),
    url='https://github.com/paul-nechifor/word_cloud',
    packages=['wordcloud'],
    package_data={'wordcloud': ['stopwords']}
)

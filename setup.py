import io
from setuptools import setup
from setuptools.extension import Extension
import versioneer

from Cython.Build import cythonize

with io.open('README.md', encoding='utf_8') as fp:
    readme = fp.read()

setup(
    author="Andreas Mueller",
    author_email="t3kcit+wordcloud@gmail.com",
    name='wordcloud',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url='https://github.com/amueller/word_cloud',
    description='A little word cloud generator',
    long_description=readme,
    long_description_content_type='text/markdown; charset=UTF-8',
    license='MIT',
    install_requires=['numpy>=1.6.1', 'pillow', 'matplotlib'],
    ext_modules=cythonize("wordcloud/query_integral_image.pyx"),
    entry_points={'console_scripts': ['wordcloud_cli=wordcloud.__main__:main']},
    packages=['wordcloud'],
    package_data={'wordcloud': ['stopwords', 'DroidSansMono.ttf']}
)

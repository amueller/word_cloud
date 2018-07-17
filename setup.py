import re
import io
from setuptools import setup
from setuptools.extension import Extension

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('wordcloud/__init__.py', encoding='utf_8').read()
    ).group(1)


with io.open('README.md', encoding='utf_8') as fp:
    readme = fp.read()

setup(
    author="Andreas Mueller",
    author_email="t3kcit+wordcloud@gmail.com",
    name='wordcloud',
    version=__version__,
    url='https://github.com/amueller/word_cloud',
    description='A little word cloud generator',
    long_description=readme,
    long_description_content_type='text/markdown; charset=UTF-8',
    license='MIT',
    install_requires=['numpy>=1.6.1', 'pillow'],
    test_requires=['matplotlib'],
    ext_modules=[Extension("wordcloud.query_integral_image",
                           ["wordcloud/query_integral_image.c"])],
    scripts=['wordcloud/wordcloud_cli.py'],
    packages=['wordcloud'],
    package_data={'wordcloud': ['stopwords', 'DroidSansMono.ttf']}
)

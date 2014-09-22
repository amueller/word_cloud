#!/usr/bin/env python2

from os import path
from wordcloud import WordCloud

d = path.dirname(__file__)

# Read the whole text.
text = open(path.join(d, 'constitution.txt')).read()
wordcloud = WordCloud().generate(text)
# Draw the positioned words to a PNG file.
wordcloud.to_file(path.join(d, 'constitution.png'))

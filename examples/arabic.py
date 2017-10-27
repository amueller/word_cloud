#!/usr/bin/env python
"""
Example using Arabic
===============
Generating a wordcloud from Arabic text
Other dependencies: bidi.algorithm, arabic_reshaper
"""

from os import path
import codecs
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display

d = path.dirname(__file__)

# Read the whole text.
f = codecs.open(path.join(d, 'arabicwords.txt'), 'r', 'utf-8')

# Make text readable for a non-Arabic library like wordcloud
text = arabic_reshaper.reshape(f.read())
text = get_display(text)

# Generate a word cloud image
# Requires Arabic font; replace "arabtype.ttf" with your 
# Arabic or other unicode font of choice
wordcloud = WordCloud(font_path='arabtype.ttf').generate(text)
wordcloud.to_file("arabic_example.png")
#!/usr/bin/env python
"""
Create wordcloud with Arabic
===============
Generating a wordcloud from Arabic text

Dependencies:
- bidi.algorithm
- arabic_reshaper

Dependencies installation:
pip install python-bidi arabic_reshape
"""

import os
import codecs
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Read the whole text.
f = codecs.open(os.path.join(d, 'arabicwords.txt'), 'r', 'utf-8')

# Make text readable for a non-Arabic library like wordcloud
text = arabic_reshaper.reshape(f.read())
text = get_display(text)

# Generate a word cloud image
wordcloud = WordCloud(font_path='fonts/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf').generate(text)

# Export to an image
wordcloud.to_file("arabic_example.png")

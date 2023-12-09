#!/usr/bin/env python
"""
Create wordcloud with Arabic
===============
Generating a wordcloud from Arabic text

Proper font is needed otherwise text might not be displayed probably
"""

import os
import codecs
from wordcloud import WordCloud

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Read the whole text.
f = codecs.open(os.path.join(d, 'arabicwords.txt'), 'r', 'utf-8')
text = f.read()

# Generate a word cloud image
wordcloud = WordCloud(font_path='fonts/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf').generate(text)

# Export to an image
wordcloud.to_file("arabic_example.png")

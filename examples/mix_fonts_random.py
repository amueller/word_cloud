#!/usr/bin/env python
"""
Mix Fonts with Random Draw Example
==================================

Generating a word cloud from the US constitution. The words are
rendered with a font randomly picked from a list.

"""
import os

import matplotlib.pyplot as plt

from wordcloud import WordCloud


# get data directory (using getcwd() is needed to support running
# example in generated IPython notebook).
d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# read the whole text.
text = open(os.path.join(d, 'constitution.txt')).read()

# provide paths to fonts for random draw.
font_paths = [
    "../wordcloud/DroidSansMono.ttf",
    "fonts/Symbola/Symbola.ttf",
    "fonts/SourceHanSerif/SourceHanSerifK-Light.otf"
]

# generate a word cloud image.
wc = WordCloud(width=1200, height=600, font_path=font_paths).generate(text)

# generate an svg outout.
with open(os.path.splitext(os.path.basename(__file__))[0] + ".svg", 'w') as f:
    f.write(wc.to_svg(embed_font=True))

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

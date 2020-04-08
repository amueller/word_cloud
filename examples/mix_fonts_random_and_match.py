#!/usr/bin/env python
"""
Mix Fonts with Random Draw Example and Match
============================================

Generating a word cloud from the US constitution. The words are
rendered with a font randomly picked from a list except for CJK
characters, to which a CJK font is applied.

"""
import os
import regex as re
from collections import defaultdict

import matplotlib.pyplot as plt

from wordcloud import MixedFontPattern
from wordcloud import STOPWORDS
from wordcloud import WordCloud


# get data directory (using getcwd() is needed to support running
# example in generated IPython notebook).
d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# read the whole text.
text = open(os.path.join(d, 'constitution.txt')).read()

wordfreq = defaultdict(int)
for word in text.split():
    word = word.strip('.,')
    if word.lower() not in STOPWORDS:
        wordfreq[word] += 1

# add some cjk language entries for demonstrating font matching
for phrase, n in {'アメリカ': 40, '憲法': 35, '大統領': 32, '合衆国': 30,
                  'あめりか': 30, 'けんぽう': 25, 'だいとうりょう': 23,
                  'がっしゅうこく': 20}.items():
    wordfreq[phrase] += n

# provide paths to fonts for random draw plus cjk font when word matches
font_paths = [
    "../wordcloud/DroidSansMono.ttf",
    "fonts/Symbola/Symbola.ttf",
    "fonts/SourceHanSerif/SourceHanSerifK-Light.otf",
    MixedFontPattern(re.compile(r"[\p{Han}\p{Katakana}\p{Hiragana}]+"),
                     "fonts/SourceHanSerif/SourceHanSerifK-Light.otf")
]

# generate a word cloud image.
wc = WordCloud(width=1200, height=600, font_path=font_paths)
wc.generate_from_frequencies(wordfreq)

# generate an svg outout.
with open(os.path.splitext(os.path.basename(__file__))[0] + ".svg", 'w') as f:
    f.write(wc.to_svg(embed_font=True))

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

#!/usr/bin/env python
"""
Using min words analyse A New Hope
===================
"""

from os import path, getcwd
import matplotlib.pyplot as plt

from wordcloud import WordCloud

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else getcwd()

# movie script of "a new hope"
# http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html
# May the lawyers deem this fair use.
text = open(path.join(d, 'a_new_hope.txt')).read()

wc = WordCloud(max_words=1000, margin=10,
               random_state=1, min_word_length=5).generate(text)
#wc.to_file("min_word_length_a_new_hope.png")
plt.imshow(wc)
plt.axis("off")
plt.show()

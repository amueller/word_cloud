#!/usr/bin/env python
"""
Using bigrams and from_frequencies
==================================
We are using a custom tokenizer (here implemented from scratch, it's recommended to
use nltk, spacy or scikit-learn instead), to allow the inclusion of word-pairs
(bigrams, 2-grams) into the word cloud.

The ``from_frequencies`` method allows generating wordclouds from a list or
array of ``(word, frequency)`` tuples, where ``word`` can be any string, and
``frequency`` can be any int or float.


We are using the likelihood ratio score developed by Dunning to find "collocations",
which are phrases made up of two or more words (we only consider two here).
If the chance that a bigram is a collocation is high, we discount the appearances
of the single words -- otherwise they would always be at least as big as the bigram.

"""


import numpy as np
from PIL import Image
from os import path
import matplotlib.pyplot as plt
import random
from itertools import tee
from collections import defaultdict
import re
from math import log

from wordcloud import WordCloud, STOPWORDS


# dunning's likelihood ratio with notation from
# http://nlp.stanford.edu/fsnlp/promo/colloc.pdf


def l(k, n, x):
    return log(max(x, 1e-10)) * k + log(max(1 - x, 1e-10)) * (n - k)


def score(bigram, counts, n_words):
    N = n_words
    c12 = counts[bigram]
    c1 = counts[bigram[0]]
    c2 = counts[bigram[1]]
    p = c2 / N
    p1 = c12 / c1
    p2 = (c2 - c12) / (N - c1)
    score = l(c12, c1, p) + l(c2 - c12, N - c1, p) - l(c12, c1, p1) - l(c2 - c12, N - c1, p2)
    return -2 * score


def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def pairwise(iterable):
    # from itertool recipies
    # is -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def unigrams_and_bigrams(text, stopwords=None):
    stopwords = [s.lower() for s in stopwords] if stopwords is not None else []
    words = re.findall(r"\w[\w']+", text)
    # remove stopwords
    words = [word for word in words if word.lower() not in stopwords]
    # remove 's
    words = [word[:-2] if word.lower().endswith("'s") else word for word in words]
    # fix for movie-script upper case names
    words = [word if not word.isupper() else word.title() for word in words]
    n_words = len(words)
    # make tuples of two words following each other
    bigrams = list(pairwise(words))
    counts_unigrams = defaultdict(int)
    counts_bigrams = defaultdict(int)
    for word in words:
        counts_unigrams[word] += 1
    for bigram in bigrams:
        # join tuples by a space
        counts_bigrams[bigram] += 1

    counts_all = {}
    counts_all.update(counts_unigrams)
    counts_all.update(counts_bigrams)

    # decount words inside bigrams
    for bigram in counts_bigrams.keys():
        # collocation detection (30 is arbitrary):
        if score(bigram, counts_all, n_words) > 30:
            counts_unigrams[bigram[0]] -= counts_bigrams[bigram]
            counts_unigrams[bigram[1]] -= counts_bigrams[bigram]
        # add joined bigram into unigrams
        counts_unigrams[' '.join(bigram)] = counts_bigrams[bigram]
    return counts_unigrams


d = path.dirname(__file__)

# read the mask image
# taken from
# http://www.stencilry.org/stencils/movies/star%20wars/storm-trooper.gif
mask = np.array(Image.open(path.join(d, "stormtrooper_mask.png")))

# movie script of "a new hope"
# http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html
# May the lawyers deem this fair use.
text = open("a_new_hope.txt").read()

# preprocessing the text a little bit
text = text.replace("INT", "")
text = text.replace("EXT", "")

wc = WordCloud(max_words=1000, mask=mask, margin=10,
               color_func=grey_color_func, random_state=3)
# from_freqencies ignores "stopwords" so we have to do it ourselves
wc.generate_from_frequencies(unigrams_and_bigrams(text, STOPWORDS).items())
plt.imshow(wc)
wc.to_file("a_new_hope_bigrams.png")
plt.axis("off")
plt.show()

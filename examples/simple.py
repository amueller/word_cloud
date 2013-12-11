#!/usr/bin/env python2

from os import path
import sys
import wordcloud

d = path.dirname(__file__)

# Read the whole text.
text = open(path.join(d, 'constitution.txt')).read()
# Separate into a list of (word, frequency).
words = wordcloud.process_text(text)
# Compute the position of the words.
elements = wordcloud.fit_words(words)
# Draw the positioned words to a PNG file.
wordcloud.draw(elements, path.join(d, 'constitution.png'))

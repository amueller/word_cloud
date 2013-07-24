#!/usr/bin/env python2

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import wordcloud

text = open('alice.txt').read()
words, counts = wordcloud.process_text(text, max_features=2000)
elements = wordcloud.fit_words(words, counts, width=500, height=500)
wordcloud.draw(elements, 'alice.png', width=500, height=500, scale=2)

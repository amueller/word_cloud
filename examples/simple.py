#!/usr/bin/env python2

import sys
import os
import wordcloud

text = open('constitution.txt').read()
words, counts = wordcloud.process_text(text)
elements = wordcloud.fit_words(words, counts)
wordcloud.draw(elements, 'constitution.png')

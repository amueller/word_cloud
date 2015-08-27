#!/usr/bin/env python2
"""
Phrase Example
===============
Generating a wordcloud from the lyrics of 'She'll be coming round the mountain' 
while having some key phrases treated as single words.
"""

from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud

d = path.dirname(__file__)

# Read the whole text.
text = open(path.join(d, 'round the mountain.txt')).read()
# A list of phrases of words we don't want spit up:
phrases = [
			"she'll be",
			"round the ",
			"when she "
		  ]
# Replace the spaces in these all occurences of these phrases with underscores		  
for s in phrases:
	text = text.replace(s,s.replace(' ','_'))
	
wordcloud = WordCloud().generate(text)
# Open a plot of the generated image.
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

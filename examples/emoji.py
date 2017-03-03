#!/usr/bin/env python
"""
Emoji Example
===============
A simple example that includes emoji.  Note that this example does not seem to work on OS X, but does
work correctly in Ubuntu
"""
import io
from os import path
from wordcloud import WordCloud

d = path.dirname(__file__)

# It is important to use io.open to correctly load the file as UTF-8
text = io.open(path.join(d, 'happy-emoji.txt')).read()

# Generate a word cloud image
# The Symbola font includes most emoji
wordcloud = WordCloud(font_path=path.join(d, 'fonts', 'Symbola', 'Symbola.ttf')).generate(text)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

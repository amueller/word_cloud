#!/usr/bin/env python3
"""
Minimal Example
===============
Generating a square wordcloud from the US constitution using a custom palette from an image.
"""

##

from os import path
from wordcloud import WordCloud,  ImagePaletteGenerator
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

d = path.dirname(__file__)
##
# Read the whole text.
text = open(path.join(d, 'constitution.txt')).read()

# Create palette from image
palette_imagefile =  path.join(d, 'cheeremo.jpg')
ipc_from_filename = ImagePaletteGenerator().add_image(palette_imagefile, 5)

# Generate a word cloud image
wordcloud = WordCloud().generate(text)
wordcloud.recolor(color_func=ipc_from_filename)
plt.imshow(wordcloud)
plt.axis("off")

# Create palette from array
palette_image =  np.array(Image.open(path.join(d, 'vintage.jpg')))
ipc_from_array = ImagePaletteGenerator().add_image(palette_image,5)
wordcloud.recolor(color_func=ipc_from_array)
# Display the generated image:
# the matplotlib way:
plt.imshow(wordcloud)
plt.axis("off")

# Create palette from multiple images
palette_imagefile_emo =  path.join(d, 'cheeremo.jpg')
palette_imagefile_vintage =  path.join(d, 'vintage.jpg')
ipc_from_multiple_files = ImagePaletteGenerator().add_image(palette_imagefile_vintage,5).add_image(palette_imagefile_emo,5)
wordcloud.recolor(color_func=ipc_from_multiple_files)
plt.imshow(wordcloud)
plt.axis("off")

# The pil way (if you don't have matplotlib)
#image = wordcloud.to_image()
#image.show()

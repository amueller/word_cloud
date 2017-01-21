#!/usr/bin/env python
"""
Transparent wordcloud
================
Using a masked wordcloud as alpha channel.
"""

from __future__ import print_function
import os.path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from wordcloud import WordCloud

d = os.path.dirname(os.path.abspath(__file__))

# Read the wordcloud source code.
word_list = []
source_dir = os.path.join(d, "..", "wordcloud")
for filename in os.listdir(source_dir):
    if filename.endswith(".py"):
        with open(os.path.join(source_dir, filename)) as file:
            word_list.append(file.read())

# image take from https://pixabay.com/en/cloud-day-dark-cludy-weather-37010/
# CC0 Public Domain
cloud_image = np.array(Image.open(os.path.join(d, "cloud.png")))

def white(*args, **kwargs):
    return "rgb(255, 255, 255)"

wc = WordCloud(
        background_color="black",
        max_words=1000,
        mask=cloud_image[...,0],
        color_func=white
        )

# generate word cloud
wc.generate('\n'.join(word_list))

# black-and-white wordcloud monochannel image
wordcloud_bw = wc.to_array()[..., 0]

# tweak the alpha value, that's where you can play a bit!
# 255 is fully transparent, 1 is opaque (text shows in white)
# This removes interpolated edges between text and background.
wordcloud_bw[wordcloud_bw > 0] = 150

# Substitute the alpha channel. This shows the wordcloud 'punched out' from the
# base image.
cloud_image[..., 3] = wordcloud_bw

# store to file in PNG format to conserve transparency
plt.imsave(os.path.join(d, "transparent_cloud.png"), cloud_image)

fig, axes = plt.subplots(1, 3)
axes[0].imshow(wordcloud_bw, cmap="gray")
axes[0].set_axis_off()
axes[1].imshow(cloud_image)
axes[1].set_axis_off()

# another option is to show the background image between the text
wordcloud_bw[wordcloud_bw == 0] = 255
cloud_image[..., 3] = wordcloud_bw
axes[2].imshow(cloud_image)
axes[2].set_axis_off()
plt.show()

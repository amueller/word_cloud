#!/usr/bin/env python3
"""
Using Gutenberg project as a text source
========================================

Connecting to Gutenberg project website in order to download
free e-book content for processing with wordcloud.
"""

# various imports for...
# ... reading the ebook from Gutenberg and removing special chars and nums
import urllib.request
from string import punctuation, digits

# ... processing image data for masking the cloud shape
import os
import numpy as np
from PIL import Image

# ... creating the word cloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# cwd, assuming stopwords default list and image are in the current path
d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()


# provide URL to an utf-8 encoded e-book on the web
# here project Gutenberg does the job
ebook_url = "https://www.gutenberg.org/files/1342/1342-0.txt"


# connect to Gutenberg website and download the ebook
book = ""
req = urllib.request.Request(url=ebook_url)
with urllib.request.urlopen(req) as f:
    book = f.read().decode('utf-8')


# strip original text from any unwanted punctuation or digits
unwanted_chars = punctuation + digits + '"“”'
book = book.translate(str.maketrans('', '', unwanted_chars)).lower()


# load some default stopword list taken from https://www.ranks.nl/stopwords,
#   combine with the wordcloud package provided list
#   & define additional stopwords as needed
with open(os.path.join(d, "stopwords_english.txt")) as f:
    stopwords = f.read().splitlines()
stopwords = STOPWORDS.union(stopwords)
stopwords.add("chapter")
stopwords.add("ebook")
stopwords.add("project")


# assess frequencies of words, we'll extend the max number of them used in the
# cloud to 50% of the words found within the given book
words_dict = {}
for word in book.split():
    if word in stopwords:
        continue
    if word in words_dict.keys():
        words_dict[word] += 1
    else:
        words_dict[word] = 1
max_words = int(0.5 * len(words_dict))


# load masking image for defining exterior shape and word coloring
img_mask = np.array(Image.open(os.path.join(d, "book_color.png")))


# put it all together including the coloring part
wc = WordCloud(background_color="white", mask=img_mask,
               stopwords=stopwords, max_words=max_words,
               contour_width=3, contour_color="black", random_state=42)
wc.generate_from_frequencies(words_dict)
image_colors = ImageColorGenerator(img_mask)
wc.recolor(color_func=image_colors)
wc.to_file("gutenberg.png")

# Author: Andreas Christian Mueller <amueller@ais.uni-bonn.de>
# (c) 2012
# Modified by: Paul Nechifor <paul@nechifor.net>
#
# License: MIT

import random
import os
import sys
import re
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from query_integral_image import query_integral_image

FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
        'stopwords')).read().split('\n')])

def fit_words(words, font_path=None, width=400, height=200,
                   margin=5, ranks_only=False, prefer_horiz=0.90):
    """Generate the positions for words.

    Parameters
    ----------
    words : array of tuples
        A tuple contains the word and its frequency.
    
    font_path : string
        Font path to the font that will be used (OTF or TTF).
        Defaults to DroidSansMono path, but you might not have it.

    width : int (default=400)
        Width of the canvas.

    height : int (default=200)
        Height of the canvas.

    ranks_only : boolean (default=False)
        Only use the rank of the words, not the actual counts.

    prefer_horiz : float (default=0.90)
        The ratio of times to try horizontal fitting as opposed to vertical.

    Notes
    -----
    Larger canvases with make the code significantly slower. If you need a large
    word cloud, run this function with a lower canvas size, and draw it with a
    larger scale.
    
    In the current form it actually just uses the rank of the counts, i.e. the
    relative differences don't matter. Play with setting the font_size in the
    main loop for different styles.
    """
    
    if len(words) <= 0:
        print("We need at least 1 word to plot a word cloud, got %d."
                % len(words))

    if font_path is None:
        font_path = FONT_PATH

    if not os.path.exists(font_path):
        raise ValueError("The font %s does not exist." % font_path)
    
    # create image
    img_grey = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img_grey)
    integral = np.zeros((height, width), dtype=np.uint32)
    img_array = np.asarray(img_grey)
    font_sizes, positions, orientations = [], [], []
    
    # intitiallize font size "large enough"
    font_size = height
    
    # start drawing grey image
    for word, count in words:
        # alternative way to set the font size
        if not ranks_only:
            font_size = min(font_size, int(100 * np.log(count + 100)))
        while True:
            # try to find a position
            font = ImageFont.truetype(font_path, font_size)
            # transpose font optionally
            if random.random() < prefer_horiz:
                orientation = None
            else:
                orientation = Image.ROTATE_90
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            # get size of resulting text
            box_size = draw.textsize(word)
            # find possible places using integral image:
            result = query_integral_image(integral, box_size[1] + margin,
                                          box_size[0] + margin)
            if result is not None or font_size == 0:
                break
            # if we didn't find a place, make font smaller
            font_size -= 1

        if font_size == 0:
            # we were unable to draw any more
            break

        x, y = np.array(result) + margin // 2
        # actually draw the text
        draw.text((y, x), word, fill="white")
        positions.append((x, y))
        orientations.append(orientation)
        font_sizes.append(font_size)
        # recompute integral image
        img_array = np.asarray(img_grey)
        # recompute bottom right
        # the order of the cumsum's is important for speed ?!
        partial_integral = np.cumsum(np.cumsum(img_array[x:, y:], axis=1),
                                     axis=0)
        # paste recomputed part into old image
        # if x or y is zero it is a bit annoying
        if x > 0:
            if y > 0:
                partial_integral += (integral[x - 1, y:]
                                     - integral[x - 1, y - 1])
            else:
                partial_integral += integral[x - 1, y:]
        if y > 0:
            partial_integral += integral[x:, y - 1][:, np.newaxis]

        integral[x:, y:] = partial_integral

    return zip(words, font_sizes, positions, orientations)

def random_color_func(word, font_size, position, orientation):
    return "hsl(%d" % random.randint(0, 255) + ", 80%, 50%)"

def draw(elements, file_name, font_path=None, width=400, height=200, scale=1,
        color_func=random_color_func):
        
    if font_path is None:
        font_path = FONT_PATH
        
    img = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(img)
    for (word, count), font_size, position, orientation in elements:
        font = ImageFont.truetype(font_path, font_size * scale)
        transposed_font = ImageFont.TransposedFont(font,
                                                   orientation=orientation)
        draw.setfont(transposed_font)
        color = color_func(word, font_size, position, orientation)
        pos = (position[1] * scale, position[0] * scale)
        draw.text(pos, word, fill=color)
    img.save(file_name)

def process_text(text, max_features=200, stopwords=None):
    """Splits a long text into words, eliminates the stopwords and returns
    (words, counts) which is necessary for make_wordcloud().

    Parameters
    ----------
    text : string
        The text to be processed.
    
    max_features : number (default=200)
        The maximum number of words.
        
    stopwords : set of strings
        The words that will be eliminated.
        
    Notes
    -----
    There are better ways to do word tokenization, but I don't want to include
    all those things.
    """
    
    if stopwords is None:
        stopwords = STOPWORDS
    
    d = {}
    for word in re.findall(r"\w[\w']*", text):
        word_lower = word.lower()
        if word_lower in stopwords:
            continue

        # Look in lowercase dict.
        if d.has_key(word_lower):
            d2 = d[word_lower]
        else:
            d2 = {}
            d[word_lower] = d2

        # Look in any case dict.
        if d2.has_key(word):
            d2[word] += 1
        else:
            d2[word] = 1

    d3 = {}
    for d2 in d.values():
        # Get the most popular case.
        first = sorted(d2.iteritems(), key=lambda x: x[1], reverse=True)[0][0]
        d3[first] = sum(d2.values())

    words = sorted(d3.iteritems(), key=lambda x: x[1], reverse=True)
    words = words[:max_features]
    maximum = float(max(d3.values()))
    for i, (word, count) in enumerate(words):
        words[i] = word, count/maximum
    
    return words

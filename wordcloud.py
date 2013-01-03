# Author: Andreas Christian Mueller <amueller@ais.uni-bonn.de>
# (c) 2012
#
# License: MIT

import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
from query_integral_image import query_integral_image

FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"


def make_wordcloud(words, counts, font_path, fname, width=400, height=200,
                   margin=5):
    # sort words by counts
    inds = np.argsort(counts)[::-1]
    counts = counts[inds]
    words = words[inds]
    # create image
    img_grey = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img_grey)
    integral = np.zeros((height, width), dtype=np.uint32)
    img_array = np.asarray(img_grey)
    font_sizes, positions, orientations = [], [], []
    # intitiallize fontsize "large enough"
    font_size = 1000
    # start drawing grey image
    for word, count in zip(words, counts):
        # set font size
        #font_size = min(font_size, int(100 * np.log(count + 100)))
        while True:
            # try to find a position
            font = ImageFont.truetype(font_path, font_size)
            # transpose font optionally
            orientation = random.choice([None, Image.ROTATE_90])
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

    # redraw in color
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    everything = zip(words, font_sizes, positions, orientations)
    for word, font_size, position, orientation in everything:
        font = ImageFont.truetype(font_path, font_size)
        # transpose font optionally
        transposed_font = ImageFont.TransposedFont(font,
                                                   orientation=orientation)
        draw.setfont(transposed_font)
        draw.text((position[1], position[0]), word,
                  fill="hsl(%d" % random.randint(0, 255) + ", 80%, 50%)")
    img.show()
    img.save(fname)


def normalise_make_wordcloud(words, counts, fname, font_path=FONT_PATH, width=800, height=600):
    """Normalise counts to be >0 and <=1 then create the wordcloud

    words is an array of the words to draw
    counts is an array of the frequency of each word
    fname is the filename for output e.g. "constitution_.png"
    font_path points at a valid system font
    """
    # normalise counts to the interval (0..1] (>0.0, <=1.0)
    counts = counts / float(counts.max())

    make_wordcloud(words, counts, font_path, width=width, height=height, fname=fname)
    return counts


if __name__ == "__main__":

    import os
    import sys

    sources = ([arg for arg in sys.argv[1:] if os.path.exists(arg)]
               or ["constitution.txt"])
    lines = []
    for s in sources:
        with open(s) as f:
            lines.extend(f.readlines())
    text = "".join(lines)

    cv = CountVectorizer(min_df=1, charset_error="ignore",
                         stop_words="english", max_features=200)
    counts = cv.fit_transform([text]).toarray().ravel()
    words = np.array(cv.get_feature_names())
    # throw away some words, normalize
    words = words[counts > 1]
    counts = counts[counts > 1]
    if len(counts) > 0:
        output_filename = os.path.splitext(os.path.basename(sources[0]))[0] + "_.png"
        counts = normalise_make_wordcloud(words, counts, output_filename)
    else:
        print "We need at least 1 word to plot a word cloud, we have {}.".format(len(counts))

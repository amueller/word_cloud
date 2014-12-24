# Author: Andreas Christian Mueller <amueller@ais.uni-bonn.de>
# (c) 2012
# Modified by: Paul Nechifor <paul@nechifor.net>
#
# License: MIT

from random import Random
import os
import re
import sys
import numpy as np
from operator import itemgetter

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from .query_integral_image import query_integral_image

item1 = itemgetter(1)

FONT_PATH = os.environ.get("FONT_PATH", "/usr/share/fonts/truetype/droid/DroidSansMono.ttf")
STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                                      'stopwords')).read().split('\n')])


def random_color_func(word, font_size, position, orientation, random_state=None):
    """Random hue color generation.

    Default coloring method. This just picks a random hue with value 80% and
    lumination 50%.

    Parameters
    ----------
    word, font_size, position, orientation  : ignored.

    random_state : random.Random object or None, (default=None)
        If a random object is given, this is used for generating random numbers.

    """
    if random_state is None:
        random_state = Random()
    return "hsl(%d, 80%%, 50%%)" % random_state.randint(0, 255)


class WordCloud(object):
    """Word cloud object for generating and drawing.

    Parameters
    ----------
    font_path : string
        Font path to the font that will be used (OTF or TTF).
        Defaults to DroidSansMono path on a Linux machine. If you are on
        another OS or don't have this font, you need to adjust this path.

    width : int (default=400)
        Width of the canvas.

    height : int (default=200)
        Height of the canvas.

    ranks_only : boolean (default=False)
        Only use the rank of the words, not the actual counts.

    prefer_horizontal : float (default=0.90)
        The ratio of times to try horizontal fitting as opposed to vertical.

    mask : nd-array or None (default=None)
        If not None, gives a binary mask on where to draw words. All zero
        entries will be considered "free" to draw on, while all non-zero
        entries will be deemed occupied. If mask is not None, width and height will be
        ignored and the shape of mask will be used instead.

    max_words : number (default=200)
        The maximum number of words.

    stopwords : set of strings
        The words that will be eliminated.

    background_color : color value (default="black")
        Background color for the word cloud image.

    max_font_size : int or None (default=None)
        Maximum font size for the largest word. If None, height of the image is
        used.

    Attributes
    ----------
    words_ : list of tuples (string, float)
        Word tokens with associated frequency.

    layout_ : list of tuples (string, int, (int, int), int, color))
        Encodes the fitted word cloud. Encodes for each word the string, font
        size, position, orientation and color.
    """

    def __init__(self, font_path=None, width=400, height=200, margin=5,
                 ranks_only=False, prefer_horizontal=0.9, mask=None, scale=1,
                 color_func=random_color_func, max_words=200, stopwords=None,
                 random_state=None, background_color='black', max_font_size=None):
        if stopwords is None:
            stopwords = STOPWORDS
        if font_path is None:
            font_path = FONT_PATH
        self.font_path = font_path
        self.width = width
        self.height = height
        self.margin = margin
        self.ranks_only = ranks_only
        self.prefer_horizontal = prefer_horizontal
        self.mask = mask
        self.scale = scale
        self.color_func = color_func
        self.max_words = max_words
        self.stopwords = stopwords
        if isinstance(random_state, int):
            random_state = Random(random_state)
        self.random_state = random_state
        self.background_color = background_color
        if max_font_size is None:
            max_font_size = height
        self.max_font_size = max_font_size

    def fit_words(self, words):
        """Generate the positions for words.

        Parameters
        ----------
        words : array of tuples
            A tuple contains the word and its frequency.

        Returns
        -------
        layout_ : list of tuples (string, int, (int, int), int, color))
            Encodes the fitted word cloud. Encodes for each word the string, font
            size, position, orientation and color.

        Notes
        -----
        Larger canvases with make the code significantly slower. If you need a large
        word cloud, run this function with a lower canvas size, and draw it with a
        larger scale.

        In the current form it actually just uses the rank of the counts, i.e. the
        relative differences don't matter. Play with setting the font_size in the
        main loop for different styles.
        """
        if self.random_state is not None:
            random_state = self.random_state
        else:
            random_state = Random()

        if len(words) <= 0:
            print("We need at least 1 word to plot a word cloud, got %d."
                  % len(words))

        if self.mask is not None:
            width = self.mask.shape[1]
            height = self.mask.shape[0]
            # the order of the cumsum's is important for speed ?!
            integral = np.cumsum(np.cumsum(self.mask, axis=1), axis=0).astype(np.uint32)
        else:
            height, width = self.height, self.width
            integral = np.zeros((height, width), dtype=np.uint32)

        # create image
        img_grey = Image.new("L", (width, height))
        draw = ImageDraw.Draw(img_grey)
        img_array = np.asarray(img_grey)
        font_sizes, positions, orientations, colors = [], [], [], []

        font_size = self.max_font_size

        # start drawing grey image
        for word, count in words:
            # alternative way to set the font size
            if not self.ranks_only:
                font_size = min(font_size, int(100 * np.log(count + 100)))
            while True:
                # try to find a position
                font = ImageFont.truetype(self.font_path, font_size)
                # transpose font optionally
                if random_state.random() < self.prefer_horizontal:
                    orientation = None
                else:
                    orientation = Image.ROTATE_90
                transposed_font = ImageFont.TransposedFont(font,
                                                           orientation=orientation)
                draw.setfont(transposed_font)
                # get size of resulting text
                box_size = draw.textsize(word)
                # find possible places using integral image:
                result = query_integral_image(integral, box_size[1] + self.margin,
                                              box_size[0] + self.margin, random_state)
                if result is not None or font_size == 0:
                    break
                # if we didn't find a place, make font smaller
                font_size -= 1

            if font_size == 0:
                # we were unable to draw any more
                break

            x, y = np.array(result) + self.margin // 2
            # actually draw the text
            draw.text((y, x), word, fill="white")
            positions.append((x, y))
            orientations.append(orientation)
            font_sizes.append(font_size)
            colors.append(self.color_func(word, font_size, (x, y), orientation,
                                          random_state=random_state))
            # recompute integral image
            if self.mask is None:
                img_array = np.asarray(img_grey)
            else:
                img_array = np.asarray(img_grey) + self.mask
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

        self.layout_ = list(zip(words, font_sizes, positions, orientations, colors))
        return self.layout_

    def process_text(self, text):
        """Splits a long text into words, eliminates the stopwords.

        Parameters
        ----------
        text : string
            The text to be processed.

        Returns
        -------
        words : list of tuples (string, float)
            Word tokens with associated frequency.


        Notes
        -----
        There are better ways to do word tokenization, but I don't want to
        include all those things.
        """

        d = {}
        flags = re.UNICODE if sys.version < '3' and \
                                type(text) is unicode else 0
        for word in re.findall(r"\w[\w']*", text, flags=flags):
            if word.isdigit():
                continue

            word_lower = word.lower()
            if word_lower in self.stopwords:
                continue

            # Look in lowercase dict.
            if word_lower in d:
                d2 = d[word_lower]
            else:
                d2 = {}
                d[word_lower] = d2

            # Look in any case dict.
            d2[word] = d2.get(word, 0) + 1

        d3 = {}
        for d2 in d.values():
            # Get the most popular case.
            first = max(d2.items(), key=item1)[0]
            d3[first] = sum(d2.values())

        # merge plurals into the singular count (simple cases only)
        for key in list(d3.keys()):
            if key.endswith('s'):
                key_singular = key[:-1]
                if key_singular in d3:
                    val_plural = d3[key]
                    val_singular = d3[key_singular]
                    d3[key_singular] = val_singular + val_plural
                    del d3[key]

        words = sorted(d3.items(), key=item1, reverse=True)
        words = words[:self.max_words]
        maximum = float(max(d3.values()))
        for i, (word, count) in enumerate(words):
            words[i] = word, count / maximum

        self.words_ = words

        return words

    def generate(self, text):
        """Generate wordcloud from text.

        Calls process_text and fit_words.

        Returns
        -------
        self
        """
        self.process_text(text)
        self.fit_words(self.words_)
        return self

    def _check_generated(self):
        """Check if layout_ was computed, otherwise raise error."""
        if not hasattr(self, "layout_"):
            raise ValueError("WordCloud has not been calculated, call generate first.")

    def to_image(self):
        self._check_generated()
        if self.mask is not None:
            width = self.mask.shape[1]
            height = self.mask.shape[0]
        else:
            height, width = self.height, self.width

        img = Image.new("RGB", (width * self.scale, height * self.scale), self.background_color)
        draw = ImageDraw.Draw(img)
        for (word, count), font_size, position, orientation, color in self.layout_:
            font = ImageFont.truetype(self.font_path, font_size * self.scale)
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            pos = (position[1] * self.scale, position[0] * self.scale)
            draw.text(pos, word, fill=color)
        return img

    def recolor(self, random_state=None, color_func=None):
        """Recolor existing layout.

        Applying a new coloring is much faster than generating the whole wordcloud.

        Parameters
        ----------
        random_state : RandomState, int, or None, default=None
            If not None, a fixed random state is used. If an int is given, this
            is used as seed for a random.Random state.

        color_func : function or None, default=None
            Function to generate new color from word count, font size, position
            and orientation.  If None, self.color_func is used.

        Returns
        -------
        self
        """
        if isinstance(random_state, int):
            random_state = Random(random_state)
        self._check_generated()

        if color_func is None:
            color_func = self.color_func
        self.layout_ = [(word, font_size, position, orientation,
                         color_func(word, font_size, position, orientation, random_state))
                        for word, font_size, position, orientation, _ in self.layout_]
        return self

    def to_file(self, filename):
        """Export to image file.

        Parameters
        ----------
        filename : string
            Location to write to.

        Returns
        -------
        self
        """

        img = self.to_image()
        img.save(filename)
        return self

    def to_array(self):
        """Convert to numpy array.

        Returns
        -------
        image : nd-array size (width, height, 3)
            Word cloud image as numpy matrix.
        """
        return np.array(self.to_image())

    def __array__(self):
        """Convert to numpy array.

        Returns
        -------
        image : nd-array size (width, height, 3)
            Word cloud image as numpy matrix.
        """
        return self.to_array()

    def to_html(self):
        raise NotImplementedError("FIXME!!!")

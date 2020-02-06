# Author: Andreas Christian Mueller <t3kcit@gmail.com>
#
# (c) 2012
# Modified by: Paul Nechifor <paul@nechifor.net>
#
# License: MIT

from __future__ import division

import warnings
import io
import os
import re
import base64
import sys
import colorsys
import matplotlib
import numpy as np
from collections import defaultdict, namedtuple
from operator import itemgetter
from random import choice, Random
from xml.sax import saxutils

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageFont

from .query_integral_image import query_integral_image
from .tokenization import unigrams_and_bigrams, process_tokens

FILE = os.path.dirname(__file__)
FONT_PATH = os.environ.get('FONT_PATH', os.path.join(FILE, 'DroidSansMono.ttf'))
STOPWORDS = set(map(str.strip, open(os.path.join(FILE, 'stopwords')).readlines()))


class IntegralOccupancyMap(object):
    def __init__(self, height, width, mask):
        self.height = height
        self.width = width
        if mask is not None:
            # the order of the cumsum's is important for speed ?!
            self.integral = np.cumsum(np.cumsum(255 * mask, axis=1),
                                      axis=0).astype(np.uint32)
        else:
            self.integral = np.zeros((height, width), dtype=np.uint32)

    def sample_position(self, size_x, size_y, random_state):
        return query_integral_image(self.integral, size_x, size_y,
                                    random_state)

    def update(self, img_array, pos_x, pos_y):
        partial_integral = np.cumsum(np.cumsum(img_array[pos_x:, pos_y:],
                                               axis=1), axis=0)
        # paste recomputed part into old image
        # if x or y is zero it is a bit annoying
        if pos_x > 0:
            if pos_y > 0:
                partial_integral += (self.integral[pos_x - 1, pos_y:]
                                     - self.integral[pos_x - 1, pos_y - 1])
            else:
                partial_integral += self.integral[pos_x - 1, pos_y:]
        if pos_y > 0:
            partial_integral += self.integral[pos_x:, pos_y - 1][:, np.newaxis]

        self.integral[pos_x:, pos_y:] = partial_integral


def random_color_func(word=None, font_size=None, position=None,
                      orientation=None, font_path=None, random_state=None):
    """Random hue color generation.

    Default coloring method. This just picks a random hue with value 80% and
    lumination 50%.

    Parameters
    ----------
    word, font_size, position, orientation  : ignored.

    random_state : random.Random object or None, (default=None)
        If a random object is given, this is used for generating random
        numbers.

    """
    if random_state is None:
        random_state = Random()
    return "hsl(%d, 80%%, 50%%)" % random_state.randint(0, 255)


class colormap_color_func(object):
    """Color func created from matplotlib colormap.

    Parameters
    ----------
    colormap : string or matplotlib colormap
        Colormap to sample from

    Example
    -------
    >>> WordCloud(color_func=colormap_color_func("magma"))

    """
    def __init__(self, colormap):
        import matplotlib.pyplot as plt
        self.colormap = plt.cm.get_cmap(colormap)

    def __call__(self, word, font_size, position, orientation,
                 random_state=None, **kwargs):
        if random_state is None:
            random_state = Random()
        r, g, b, _ = np.maximum(0, 255 * np.array(self.colormap(
            random_state.uniform(0, 1))))
        return "rgb({:.0f}, {:.0f}, {:.0f})".format(r, g, b)


def get_single_color_func(color):
    """Create a color function which returns a single hue and saturation with.
    different values (HSV). Accepted values are color strings as usable by
    PIL/Pillow.

    >>> color_func1 = get_single_color_func('deepskyblue')
    >>> color_func2 = get_single_color_func('#00b4d2')
    """
    old_r, old_g, old_b = ImageColor.getrgb(color)
    rgb_max = 255.
    h, s, v = colorsys.rgb_to_hsv(old_r / rgb_max, old_g / rgb_max,
                                  old_b / rgb_max)

    def single_color_func(word=None, font_size=None, position=None,
                          orientation=None, font_path=None, random_state=None):
        """Random color generation.

        Additional coloring method. It picks a random value with hue and
        saturation based on the color given to the generating function.

        Parameters
        ----------
        word, font_size, position, orientation  : ignored.

        random_state : random.Random object or None, (default=None)
          If a random object is given, this is used for generating random
          numbers.

        """
        if random_state is None:
            random_state = Random()
        r, g, b = colorsys.hsv_to_rgb(h, s, random_state.uniform(0.2, 1))
        return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(r * rgb_max, g * rgb_max,
                                                    b * rgb_max)
    return single_color_func


class BoxSize(object):
    """Bounding box size for a word."""
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def scale(self, scale):
        return BoxSize(int(self.w * scale), int(self.h * scale))

    def rotate(self):
        self.w, self.h = self.h, self.w


FontOffset = namedtuple('FontOffset', 'start end path x y w h ascent descent')
"""Stores the info about the font used for the substring in the
word. Each font used for the word is given a ``FontOffset`` object,
stored in ``FontInfo.font_offsets``. This object is partly used to
align multiple fonts along the baseline, taking into account varying
ascents and descents for different fonts.

Parameters
----------
start : int
    Starting index for the substring in the word.

end : int
    Ending index + 1 for the substring in the word.

path : str
    Font path.

x : int
    x offset for the substring within the enclosing bounding box of the word.

y : int
    y offset for the substring within the enclosing bounding box of the word.

w : int
    Width of the bounding box for the substring.

h : int
    Height of the bounding box for the substring.

ascent: int
    Ascent for the font.

descent: int
    Descent for the font.

"""


MixedFontPattern = namedtuple('MixedFontPattern', 'pattern path')
"""Provide the font to be used for the matched substring in the word.

Parameters
----------
pattern : re.compile
    Regex pattern to match substring to which the font is applied.

path : str
    Font path to a font file, in either OTF or TTF.

"""


class FontCollection(object):
    """Manages the collection of fonts."""

    _image_font_cache = {}

    def __init__(self, font_paths):
        self.font_paths = []
        self.mixed_font_paths = []

        if font_paths is None:
            self.font_paths.append(FONT_PATH)
        elif isinstance(font_paths, str):
            self.font_paths = [font_paths]
        else:
            for x in font_paths:
                if isinstance(x, str):
                    self.font_paths.append(x)
                elif isinstance(x, MixedFontPattern):
                    self.mixed_font_paths.append((x.pattern, FontCollection(x.path)))

        # ensure at least one font is defined
        if len(self.font_paths) == 0:
            self.font_paths.append(FONT_PATH)

    @property
    def default_font_path(self):
        return self.font_paths[0]

    def image_font(self, path, size):
        key = (path, size)
        if key in self._image_font_cache:
            return self._image_font_cache[key]
        font = ImageFont.truetype(path, size)
        props = self._image_font_props(font)
        self._image_font_cache[key] = font, props
        return font, props

    def _image_font_props(self, font):
        raw_font_family, raw_font_style = font.getname()
        # TODO properly escape/quote this name?
        font_family = repr(raw_font_family)
        # TODO better support for uncommon font styles/weights?
        raw_font_style = raw_font_style.lower()

        if 'bold' in raw_font_style:
            font_weight = 'bold'
        else:
            font_weight = 'normal'

        if 'italic' in raw_font_style:
            font_style = 'italic'
        elif 'oblique' in raw_font_style:
            font_style = 'oblique'
        else:
            font_style = 'normal'

        FontProp = namedtuple('FontProp', 'family weight style')
        return FontProp(font_family, font_weight, font_style)

    @classmethod
    def clear_image_font_cache(cls):
        cls._image_font_cache.clear()

    def _match_font_paths(self, word):
        result = [choice(self.font_paths)] * len(word)
        if self.mixed_font_paths:
            for pattern, fontcol in reversed(self.mixed_font_paths):
                for m in pattern.finditer(word):
                    start = m.start()
                    end = m.end()
                    subresult = fontcol._match_font_paths(word[start:end])
                    for i, font_path in zip(range(start, end), subresult):
                        result[i] = font_path
        return result

    def _pick(self, word, font_paths, font_size, orientation):
        def get_bounds(buff, current_font):
            font, _ = self.image_font(current_font, font_size)
            w, h = font.getsize(buff)
            ascent, descent = font.getmetrics()
            return (w, h), (ascent, descent)

        buff = ''
        offsets = []
        for idx, (c, font_path) in enumerate(zip(word, font_paths)):
            if buff == '':
                # init buff
                buff = c
                current_font_path = font_path
            elif font_path == current_font_path:
                buff += c
            else:
                offsets.append((idx, current_font_path,
                                get_bounds(buff, current_font_path)))

                # restart buff
                buff = c
                current_font_path = font_path
        else:
            offsets.append((idx + 1, current_font_path,
                            get_bounds(buff, current_font_path)))

            max_ascent = max(ascent for _, _, (_, (ascent, _)) in offsets)

            box_size = BoxSize(0, 0)
            font_offsets = []
            start_idx = 0
            for idx, font_path, ((w, h), (ascent, descent)) in offsets:
                x, y = [box_size.w, 0]
                if ascent < max_ascent:
                    # adjust vertical offset till baseline aligns
                    y = max_ascent - ascent
                font_offsets.append(
                    FontOffset(start_idx, idx, font_path, x, y, w, h, ascent, descent)
                )
                start_idx = idx
                box_size.w += w
                box_size.h = max(box_size.h, h + y)
        return font_offsets, box_size

    def pick(self, word, font_size, orientation):
        """Pick font(s) for the given word.

        Returns
        -------
        FontInfo

        """
        font_paths = self._match_font_paths(word)
        font_offsets, box_size = self._pick(word, font_paths, font_size, orientation)
        if orientation is not None:
            box_size.rotate()
        return FontInfo(font_offsets, font_size, box_size, orientation, self)


class FontInfo(object):
    """Helper object to collect info on the font(s) used for the word."""

    def __init__(self, font_offsets, size, box_size, orientation, font_collection):
        self.font_offsets = font_offsets
        self.size = size
        self.box_size = box_size
        self.orientation = orientation
        self.font_collection = font_collection


class LayoutItem(object):
    """Helper object to collect layout information."""

    def __init__(self, word, frequency, font_info, color, x, y):
        self.word = word
        self.frequency = frequency
        self.font_info = font_info
        self.color = color
        self.x = x
        self.y = y

    def recolor(self, color_func, random_state):
        self.color = color_func(
            word=self.word,
            font_size=self.font_info.size,
            position=(self.x, self.y),
            orientation=self.font_info.orientation,
            random_state=random_state,
            font_path=self.font_info.font_collection.default_font_path
        )


class Renderer(object):
    """Output renderer supplies the consistent interface for rendering output."""

    def __init__(self, word_cloud):
        self.wc = word_cloud

    def render(self):
        raise NotImplementedError

    def render_layout(self):
        raise NotImplementedError


class ImageRenderer(Renderer):
    """Image output renderer."""

    def __init__(self, word_cloud, draw):
        super(ImageRenderer, self).__init__(word_cloud)
        self.draw = draw

    def _get_mask(self, layout_item, scale):
        word = layout_item.word
        font_info = layout_item.font_info
        box_size = font_info.box_size.scale(scale)
        if font_info.orientation is not None:
            box_size.rotate()
        font_size = int(font_info.size * scale)

        mask_draw = ImageDraw.Draw(Image.new('L', (box_size.w, box_size.h), 0))

        for font_offset in font_info.font_offsets:
            font, _ = font_info.font_collection.image_font(font_offset.path, font_size)
            mask_draw.text((int(font_offset.x * scale), int(font_offset.y * scale)),
                           word[font_offset.start:font_offset.end],
                           fill="white",
                           font=font)

        return mask_draw.im

    def render(self):
        for layout_item in self.wc.layout_:
            self.render_layout(layout_item, self.wc.scale)

    def render_layout(self, layout_item, scale):
        font_info = layout_item.font_info
        mask = self._get_mask(layout_item, scale)

        x = int(layout_item.x * scale)
        y = int(layout_item.y * scale)

        # see ImageDraw.text
        ink, fill = self.draw._getink(layout_item.color)
        if ink is None:
            ink = fill
        if ink is not None:
            if font_info.orientation is not None:
                mask = mask.transpose(font_info.orientation)
            self.draw.draw.draw_bitmap((y, x), mask, ink)


class SVGRenderer(Renderer):
    """SVG output renderer."""

    def __init__(self,
                 word_cloud,
                 embed_font=False,
                 optimize_embedded_font=True,
                 embed_image=False):
        super(SVGRenderer, self).__init__(word_cloud)
        self.embed_font = embed_font
        self.optimize_embedded_font = optimize_embedded_font
        self.embed_image = embed_image

    def render(self):
        # TODO should add option to specify URL for font (i.e. WOFF file)

        wc = self.wc
        scale = wc.scale

        # Get max font size
        max_font_size = int(
            (max(w.font_info.size for w in wc.layout_) if wc.max_font_size is None
             else self.wc.max_font_size) * scale
        )

        # Text buffer
        result = []

        # Add header
        result.append(
            '<svg xmlns="http://www.w3.org/2000/svg"'
            ' width="{}"'
            ' height="{}"'
            '>'
            .format(int(wc.width * scale), int(wc.height * scale))
        )

        font_paths = set()

        # Embed font, if requested
        if self.embed_font:
            # Import here, to avoid hard dependency on fonttools
            import fontTools
            import fontTools.subset

            # Subset options
            options = fontTools.subset.Options(

                # Small impact on character shapes, but reduce size a lot
                hinting=not self.optimize_embedded_font,

                # On small subsets, can improve size
                desubroutinize=self.optimize_embedded_font,

                # Try to be lenient
                ignore_missing_glyphs=True,
            )

            fonts = defaultdict(set)
            for layout_item in wc.layout_:
                for font_offset in layout_item.font_info.font_offsets:
                    for c in layout_item.word[font_offset.start:font_offset.end]:
                        fonts[font_offset.path].add(c)

            for font_path, characters in fonts.items():
                font_paths.add(font_path)

                # Load and subset font
                ttf = fontTools.subset.load_font(font_path, options)
                subsetter = fontTools.subset.Subsetter(options)
                text = ''.join(characters)
                subsetter.populate(text=text)
                subsetter.subset(ttf)

                # Export as WOFF
                # TODO is there a better method, i.e. directly export to WOFF?
                buffer = io.BytesIO()
                ttf.saveXML(buffer)
                buffer.seek(0)
                woff = fontTools.ttLib.TTFont(flavor='woff')
                woff.importXML(buffer)

                _, fp = wc.font_collection.image_font(font_path, max_font_size)

                # Create stylesheet with embedded font face
                buffer = io.BytesIO()
                woff.save(buffer)
                data = base64.b64encode(buffer.getbuffer()).decode('ascii')
                url = 'data:application/font-woff;charset=utf-8;base64,' + data
                result.append(
                    '<style>'
                    '@font-face{{'
                    'font-family:{};'
                    'font-weight:{};'
                    'font-style:{};'
                    'src:url("{}")format("woff");'
                    '}}'
                    '</style>'
                    .format(
                        fp.family,
                        fp.weight,
                        fp.style,
                        url
                    )
                )

        # Add background
        if wc.background_color is not None:
            result.append(
                '<rect'
                ' width="100%"'
                ' height="100%"'
                ' style="fill:{}"'
                '>'
                '</rect>'
                .format(wc.background_color)
            )

        # Embed image, useful for debug purpose
        if self.embed_image:
            image = self.to_image()
            data = io.BytesIO()
            image.save(data, format='JPEG')
            data = base64.b64encode(data.getbuffer()).decode('ascii')
            result.append(
                '<image'
                ' width="100%"'
                ' height="100%"'
                ' href="data:image/jpg;base64,{}"'
                '/>'
                .format(data)
            )

        # Gather all the font paths used, if not already computed while embedding
        if not font_paths:
            font_paths.update(font_offset.path
                              for layout_item in wc.layout_
                              for font_offset in layout_item.font_info.font_offsets)

        # Select global style if only one font is used
        if len(font_paths) == 1:
            _, fp = wc.font_collection.image_font(list(font_paths)[0], max_font_size)
            result.append(
                '<style>text{{font-family:{};font-weight:{};font-style:{};}}</style>'
                .format(fp.family, fp.weight, fp.style)
            )
            mixed_fonts = False
        else:
            mixed_fonts = True

        # For each word in layout
        for layout_item in wc.layout_:
            result.extend(self.render_layout(layout_item, scale, mixed_fonts))

        # TODO draw contour

        # Complete SVG file
        result.append('</svg>')
        return '\n'.join(result)

    def render_layout(self, layout_item, scale, mixed_fonts=False):
        font_info = layout_item.font_info
        font_size = int(font_info.size * scale)

        result = []
        for font_offset in font_info.font_offsets:
            x = layout_item.y
            y = layout_item.x

            if font_info.orientation is None:
                x += font_offset.x
                y += font_offset.y + font_offset.ascent
            else:
                x += font_offset.y + font_offset.ascent
                y += font_info.box_size.h - font_offset.x

            transform = 'translate({},{})'.format(int(x * scale),
                                                  int(y * scale))
            if font_info.orientation is not None:
                transform += ' rotate(-90)'

            params = {
                "fill": layout_item.color,
                "font_size": font_size,
                "text_length": int(font_offset.w * scale),
                "transform": transform,
                "word": saxutils.escape(
                    layout_item.word[font_offset.start:font_offset.end]
                ),
            }
            if mixed_fonts:
                _, fp = self.wc.font_collection.image_font(font_offset.path, font_size)
                params.update(font_family=fp.family,
                              font_style=fp.style,
                              font_weight=fp.weight)
                text_prop = ('font-family="{font_family}" '
                             'font-size="{font_size}" '
                             'font-style="{font_style}" '
                             'font-weight="{font_weight}" '
                             'style="fill:{fill}" '
                             'textLength="{text_length}" '
                             'transform="{transform}"')
            else:
                text_prop = ('font-size="{font_size}" '
                             'style="fill:{fill}" '
                             'textLength="{text_length}" '
                             'transform="{transform}"')

            # Create node
            result.append(('<text ' + text_prop + '>{word}</text>').format(**params))

        return result


class WordCloud(object):
    r"""Word cloud object for generating and drawing.

    Parameters
    ----------
    font_path : str or list of str or MixedFontPattern
        Font path to the font that will be used (OTF or TTF).
        Defaults to DroidSansMono path on a Linux machine. If you are on
        another OS or don't have this font, you need to adjust this path.
        This can also be a list of str, in which case a font is randomly
        drawn from them for each word. The list can also include a
        ``MixedFontPattern``(s), in which case matched substrings in the word
        are rendered with the font specified in that object.

    width : int (default=400)
        Width of the canvas.

    height : int (default=200)
        Height of the canvas.

    prefer_horizontal : float (default=0.90)
        The ratio of times to try horizontal fitting as opposed to vertical.
        If prefer_horizontal < 1, the algorithm will try rotating the word
        if it doesn't fit. (There is currently no built-in way to get only
        vertical words.)

    mask : nd-array or None (default=None)
        If not None, gives a binary mask on where to draw words. If mask is not
        None, width and height will be ignored and the shape of mask will be
        used instead. All white (#FF or #FFFFFF) entries will be considerd
        "masked out" while other entries will be free to draw on. [This
        changed in the most recent version!]

    contour_width: float (default=0)
        If mask is not None and contour_width > 0, draw the mask contour.

    contour_color: color value (default="black")
        Mask contour color.

    scale : float (default=1)
        Scaling between computation and drawing. For large word-cloud images,
        using scale instead of larger canvas size is significantly faster, but
        might lead to a coarser fit for the words.

    min_font_size : int (default=4)
        Smallest font size to use. Will stop when there is no more room in this
        size.

    font_step : int (default=1)
        Step size for the font. font_step > 1 might speed up computation but
        give a worse fit.

    max_words : number (default=200)
        The maximum number of words.

    stopwords : set of strings or None
        The words that will be eliminated. If None, the build-in STOPWORDS
        list will be used. Ignored if using generate_from_frequencies.

    background_color : color value (default="black")
        Background color for the word cloud image.

    max_font_size : int or None (default=None)
        Maximum font size for the largest word. If None, height of the image is
        used.

    mode : string (default="RGB")
        Transparent background will be generated when mode is "RGBA" and
        background_color is None.

    relative_scaling : float (default='auto')
        Importance of relative word frequencies for font-size.  With
        relative_scaling=0, only word-ranks are considered.  With
        relative_scaling=1, a word that is twice as frequent will have twice
        the size.  If you want to consider the word frequencies and not only
        their rank, relative_scaling around .5 often looks good.
        If 'auto' it will be set to 0.5 unless repeat is true, in which
        case it will be set to 0.

        .. versionchanged: 2.0
            Default is now 'auto'.

    color_func : callable, default=None
        Callable with parameters word, font_size, position, orientation,
        font_path, random_state that returns a PIL color for each word.
        Overwrites "colormap".
        See colormap for specifying a matplotlib colormap instead.
        To create a word cloud with a single color, use
        ``color_func=lambda *args, **kwargs: "white"``.
        The single color can also be specified using RGB code. For example
        ``color_func=lambda *args, **kwargs: (255,0,0)`` sets color to red.

    regexp : string or None (optional)
        Regular expression to split the input text into tokens in process_text.
        If None is specified, ``r"\w[\w']+"`` is used. Ignored if using
        generate_from_frequencies.

    collocations : bool, default=True
        Whether to include collocations (bigrams) of two words. Ignored if using
        generate_from_frequencies.


        .. versionadded: 2.0

    colormap : string or matplotlib colormap, default="viridis"
        Matplotlib colormap to randomly draw colors from for each word.
        Ignored if "color_func" is specified.

        .. versionadded: 2.0

    normalize_plurals : bool, default=True
        Whether to remove trailing 's' from words. If True and a word
        appears with and without a trailing 's', the one with trailing 's'
        is removed and its counts are added to the version without
        trailing 's' -- unless the word ends with 'ss'. Ignored if using
        generate_from_frequencies.

    repeat : bool, default=False
        Whether to repeat words and phrases until max_words or min_font_size
        is reached.

    include_numbers : bool, default=False
        Whether to include numbers as phrases or not.

    min_word_length : int, default=0
        Minimum number of letters a word must have to be included.

    Attributes
    ----------
    ``words_`` : dict of string to float
        Word tokens with associated frequency.

        .. versionchanged: 2.0
            ``words_`` is now a dictionary

    ``layout_`` : list of LayoutItem objects
        Encodes the fitted word cloud.

    Notes
    -----
    Larger canvases with make the code significantly slower. If you need a
    large word cloud, try a lower canvas size, and set the scale parameter.

    The algorithm might give more weight to the ranking of the words
    than their actual frequencies, depending on the ``max_font_size`` and the
    scaling heuristic.
    """

    def __init__(self, font_path=None, width=400, height=200, margin=2,
                 ranks_only=None, prefer_horizontal=.9, mask=None, scale=1,
                 color_func=None, max_words=200, min_font_size=4,
                 stopwords=None, random_state=None, background_color='black',
                 max_font_size=None, font_step=1, mode="RGB",
                 relative_scaling='auto', regexp=None, collocations=True,
                 colormap=None, normalize_plurals=True, contour_width=0,
                 contour_color='black', repeat=False,
                 include_numbers=False, min_word_length=0):
        if color_func is None and colormap is None:
            version = matplotlib.__version__
            if version[0] < "2" and version[2] < "5":
                colormap = "hsv"
            else:
                colormap = "viridis"
        self.colormap = colormap
        self.collocations = collocations
        self.font_collection = FontCollection(font_path)

        if mask is not None:
            self.width = mask.shape[1]
            self.height = mask.shape[0]
        else:
            self.width = width
            self.height = height

        self.margin = margin
        self.prefer_horizontal = prefer_horizontal
        self.mask = mask
        self.contour_color = contour_color
        self.contour_width = contour_width
        self.scale = scale
        self.color_func = color_func or colormap_color_func(colormap)
        self.max_words = max_words
        self.stopwords = stopwords if stopwords is not None else STOPWORDS
        self.min_font_size = min_font_size
        self.font_step = font_step
        self.regexp = regexp
        if isinstance(random_state, int):
            random_state = Random(random_state)
        self.random_state = random_state
        self.background_color = background_color
        self.max_font_size = max_font_size
        self.mode = mode

        if relative_scaling == "auto":
            if repeat:
                relative_scaling = 0
            else:
                relative_scaling = .5

        if relative_scaling < 0 or relative_scaling > 1:
            raise ValueError("relative_scaling needs to be "
                             "between 0 and 1, got %f." % relative_scaling)
        self.relative_scaling = relative_scaling
        if ranks_only is not None:
            warnings.warn("ranks_only is deprecated and will be removed as"
                          " it had no effect. Look into relative_scaling.",
                          DeprecationWarning)
        self.normalize_plurals = normalize_plurals
        self.repeat = repeat
        self.include_numbers = include_numbers
        self.min_word_length = min_word_length

    def fit_words(self, frequencies):
        """Create a word_cloud from words and frequencies.

        Alias to generate_from_frequencies.

        Parameters
        ----------
        frequencies : dict from string to float
            A contains words and associated frequency.

        Returns
        -------
        self
        """
        return self.generate_from_frequencies(frequencies)

    def generate_from_frequencies(self, frequencies, max_font_size=None):  # noqa: C901
        """Create a word_cloud from words and frequencies.

        Parameters
        ----------
        frequencies : dict from string to float
            A contains words and associated frequency.

        max_font_size : int
            Use this font-size instead of self.max_font_size

        Returns
        -------
        self

        """
        # make sure frequencies are sorted and normalized
        frequencies = sorted(frequencies.items(), key=itemgetter(1), reverse=True)
        if len(frequencies) <= 0:
            raise ValueError("We need at least 1 word to plot a word cloud, "
                             "got %d." % len(frequencies))
        frequencies = frequencies[:self.max_words]

        # largest entry will be 1
        max_frequency = float(frequencies[0][1])

        frequencies = [(word, freq / max_frequency)
                       for word, freq in frequencies]

        if self.random_state is not None:
            random_state = self.random_state
        else:
            random_state = Random()

        boolean_mask = None if self.mask is None else self._get_bolean_mask(self.mask)
        occupancy = IntegralOccupancyMap(self.height, self.width, boolean_mask)

        # create image
        img_grey = Image.new("L", (self.width, self.height))
        img_array = np.asarray(img_grey)
        renderer = ImageRenderer(self, ImageDraw.Draw(img_grey))

        last_freq = 1.

        if max_font_size is None:
            # if not provided use default font_size
            max_font_size = self.max_font_size

        if max_font_size is None:
            # figure out a good font size by trying to draw with
            # just the first two words
            if len(frequencies) == 1:
                # we only have one word. We make it big!
                font_size = self.height
            else:
                self.generate_from_frequencies(dict(frequencies[:2]),
                                               max_font_size=self.height)
                # find font sizes
                sizes = [x.font_info.size for x in self.layout_]
                try:
                    font_size = int(2 * sizes[0] * sizes[1]
                                    / (sizes[0] + sizes[1]))
                # quick fix for if self.layout_ contains less than 2 values
                # on very small images it can be empty
                except IndexError:
                    try:
                        font_size = sizes[0]
                    except IndexError:
                        raise ValueError(
                            "Couldn't find space to draw. Either the Canvas size"
                            " is too small or too much of the image is masked "
                            "out.")
        else:
            font_size = max_font_size

        # we set self.words_ here because we called generate_from_frequencies
        # above... hurray for good design?
        self.words_ = dict(frequencies)

        if self.repeat and len(frequencies) < self.max_words:
            # pad frequencies with repeating words.
            times_extend = int(np.ceil(self.max_words / len(frequencies))) - 1
            # get smallest frequency
            frequencies_org = list(frequencies)
            downweight = frequencies[-1][1]
            for i in range(times_extend):
                frequencies.extend([(word, freq * downweight ** (i + 1))
                                    for word, freq in frequencies_org])

        layout = []

        # start drawing grey image
        for word, freq in frequencies:
            if freq == 0:
                continue
            # select the font size
            rs = self.relative_scaling
            if rs != 0:
                font_size = int(round((rs * (freq / float(last_freq))
                                       + (1 - rs)) * font_size))
            if random_state.random() < self.prefer_horizontal:
                orientation = None
            else:
                orientation = Image.ROTATE_90
            tried_other_orientation = False

            while True:
                font_info = self.font_collection.pick(word, font_size, orientation)

                # find possible places using integral image:
                result = occupancy.sample_position(font_info.box_size.h + self.margin,
                                                   font_info.box_size.w + self.margin,
                                                   random_state)

                if result is not None or font_size < self.min_font_size:
                    # either we found a place or font-size went too small
                    break
                # if we didn't find a place, make font smaller
                # but first try to rotate!
                if not tried_other_orientation and self.prefer_horizontal < 1:
                    orientation = (Image.ROTATE_90 if orientation is None else
                                   Image.ROTATE_90)
                    tried_other_orientation = True
                else:
                    font_size -= self.font_step
                    orientation = None

            if font_size < self.min_font_size:
                # we were unable to draw any more
                break

            x, y = np.array(result) + self.margin // 2
            layout_item = LayoutItem(word, freq, font_info, "white", x, y)
            renderer.render_layout(layout_item, scale=1)
            layout_item.recolor(self.color_func, random_state)
            layout.append(layout_item)

            # recompute integral image
            if self.mask is None:
                img_array = np.asarray(img_grey)
            else:
                img_array = np.asarray(img_grey) + boolean_mask
            # recompute bottom right
            # the order of the cumsum's is important for speed ?!
            occupancy.update(img_array, x, y)
            last_freq = freq

        self.layout_ = layout
        return self

    def process_text(self, text):
        """Splits a long text into words, eliminates the stopwords.

        Parameters
        ----------
        text : string
            The text to be processed.

        Returns
        -------
        words : dict (string, int)
            Word tokens with associated frequency.

        ..versionchanged:: 1.2.2
            Changed return type from list of tuples to dict.

        Notes
        -----
        There are better ways to do word tokenization, but I don't want to
        include all those things.
        """

        stopwords = set([i.lower() for i in self.stopwords])

        flags = (re.UNICODE if sys.version < '3' and type(text) is unicode  # noqa: F821
                 else 0)
        regexp = self.regexp if self.regexp is not None else r"\w[\w']+"

        words = re.findall(regexp, text, flags)
        # remove stopwords
        words = [word for word in words if word.lower() not in stopwords]
        # remove 's
        words = [word[:-2] if word.lower().endswith("'s") else word
                 for word in words]
        # remove numbers
        if not self.include_numbers:
            words = [word for word in words if not word.isdigit()]
        # remove short words
        if self.min_word_length:
            words = [word for word in words if len(word) >= self.min_word_length]

        if self.collocations:
            word_counts = unigrams_and_bigrams(words, self.normalize_plurals)
        else:
            word_counts, _ = process_tokens(words, self.normalize_plurals)

        return word_counts

    def generate_from_text(self, text):
        """Generate wordcloud from text.

        The input "text" is expected to be a natural text. If you pass a sorted
        list of words, words will appear in your output twice. To remove this
        duplication, set ``collocations=False``.

        Calls process_text and generate_from_frequencies.

        ..versionchanged:: 1.2.2
            Argument of generate_from_frequencies() is not return of
            process_text() any more.

        Returns
        -------
        self
        """
        words = self.process_text(text)
        self.generate_from_frequencies(words)
        return self

    def generate(self, text):
        """Generate wordcloud from text.

        The input "text" is expected to be a natural text. If you pass a sorted
        list of words, words will appear in your output twice. To remove this
        duplication, set ``collocations=False``.

        Alias to generate_from_text.

        Calls process_text and generate_from_frequencies.

        Returns
        -------
        self
        """
        return self.generate_from_text(text)

    def _check_generated(self):
        """Check if ``layout_`` was computed, otherwise raise error."""
        if not hasattr(self, "layout_"):
            raise ValueError("WordCloud has not been calculated, call generate"
                             " first.")

    def to_image(self):
        self._check_generated()
        img = Image.new(self.mode, (int(self.width * self.scale),
                                    int(self.height * self.scale)),
                        self.background_color)
        renderer = ImageRenderer(self, ImageDraw.Draw(img))
        renderer.render()
        return self._draw_contour(img=img)

    def recolor(self, random_state=None, color_func=None, colormap=None):
        """Recolor existing layout.

        Applying a new coloring is much faster than generating the whole
        wordcloud.

        Parameters
        ----------
        random_state : RandomState, int, or None, default=None
            If not None, a fixed random state is used. If an int is given, this
            is used as seed for a random.Random state.

        color_func : function or None, default=None
            Function to generate new color from word count, font size, position
            and orientation.  If None, self.color_func is used.

        colormap : string or matplotlib colormap, default=None
            Use this colormap to generate new colors. Ignored if color_func
            is specified. If None, self.color_func (or self.color_map) is used.

        Returns
        -------
        self
        """
        if isinstance(random_state, int):
            random_state = Random(random_state)
        self._check_generated()

        if color_func is None:
            if colormap is None:
                color_func = self.color_func
            else:
                color_func = colormap_color_func(colormap)

        for item in self.layout_:
            item.recolor(color_func, random_state)
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
        img.save(filename, optimize=True)
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

    def to_svg(self, embed_font=False, optimize_embedded_font=True, embed_image=False):
        """Export to SVG.

        Font is assumed to be available to the SVG reader. Otherwise, text
        coordinates may produce artifacts when rendered with replacement font.
        It is also possible to include a subset of the original font in WOFF
        format using ``embed_font`` (requires `fontTools`).

        Note that some renderers do not handle glyphs the same way, and may
        differ from ``to_image`` result. In particular, Complex Text Layout may
        not be supported. In this typesetting, the shape or positioning of a
        grapheme depends on its relation to other graphemes.

        Pillow, since version 4.2.0, supports CTL using ``libraqm``. However,
        due to dependencies, this feature is not always enabled. Hence, the
        same rendering differences may appear in ``to_image``. As this
        rasterized output is used to compute the layout, this also affects the
        layout generation. Use ``PIL.features.check`` to test availability of
        ``raqm``.

        Consistant rendering is therefore expected if both Pillow and the SVG
        renderer have the same support of CTL.

        Contour drawing is not supported.

        Parameters
        ----------
        embed_font : bool, default=False
            Whether to include font inside resulting SVG file.

        optimize_embedded_font : bool, default=True
            Whether to be aggressive when embedding a font, to reduce size. In
            particular, hinting tables are dropped, which may introduce slight
            changes to character shapes (w.r.t. `to_image` baseline).

        embed_image : bool, default=False
            Whether to include rasterized image inside resulting SVG file.
            Useful for debugging.

        Returns
        -------
        content : string
            Word cloud image as SVG string
        """
        self._check_generated()
        renderer = SVGRenderer(self,
                               embed_font=embed_font,
                               optimize_embedded_font=optimize_embedded_font,
                               embed_image=embed_image)
        return renderer.render()

    def _get_bolean_mask(self, mask):
        """Cast to two dimensional boolean mask."""
        if mask.dtype.kind == 'f':
            warnings.warn("mask image should be unsigned byte between 0"
                          " and 255. Got a float array")
        if mask.ndim == 2:
            boolean_mask = mask == 255
        elif mask.ndim == 3:
            # if all channels are white, mask out
            boolean_mask = np.all(mask[:, :, :3] == 255, axis=-1)
        else:
            raise ValueError("Got mask of invalid shape: %s" % str(mask.shape))
        return boolean_mask

    def _draw_contour(self, img):
        """Draw mask contour on a pillow image."""
        if self.mask is None or self.contour_width == 0:
            return img

        mask = self._get_bolean_mask(self.mask) * 255
        contour = Image.fromarray(mask.astype(np.uint8))
        contour = contour.resize(img.size)
        contour = contour.filter(ImageFilter.FIND_EDGES)
        contour = np.array(contour)

        # make sure borders are not drawn before changing width
        contour[[0, -1], :] = 0
        contour[:, [0, -1]] = 0

        # use gaussian to change width, divide by 10 to give more resolution
        radius = self.contour_width / 10
        contour = Image.fromarray(contour)
        contour = contour.filter(ImageFilter.GaussianBlur(radius=radius))
        contour = np.array(contour) > 0
        contour = np.dstack((contour, contour, contour))

        # color the contour
        ret = np.array(img) * np.invert(contour)
        if self.contour_color != 'black':
            color = Image.new(img.mode, img.size, self.contour_color)
            ret += np.array(color) * contour

        return Image.fromarray(ret)

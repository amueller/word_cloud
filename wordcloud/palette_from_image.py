import numpy as np
from PIL import ImageFont
from PIL import Image
from collections import Counter
import os.path
import random



class ImagePaletteGenerator(object):
    """Color generator based on a color image.

    Generate a color palette based on one or multiple images. Therefore, all unique colors
    are extracted and sorted by frequency. The words will be
    colored starting wit the most used color in the image.

    After construction, the object is to be filled with image colors
    and further acts as a callable that can be passed as
    color_func to the word cloud constructor or to the recolor method.

    """

    def __init__(self):
        self.color_index = 0
        self.ucolors=[]

    def add_image(self, image, max_colors = np.inf):
        """Add the colors of an image by filename or image nd-array

        Parameters
        ----------
        image : A string containing the image path or a nd-array, shape (height, width, 3).
        Alpha channels are ignored.
        max_colors : The n most used colors in the image that are to be added to the palette.

        Returns
        -------
        self : The object to allow chaining.
        """
        if isinstance(image, str):
            if os.path.isfile(image):
                try:
                     image = np.array(Image.open(image))
                except:
                     raise ValueError('Image {0} could not be opened'.format(image))
            else:
                raise ValueError('Image {0} could not be found'.format(image))
        elif image.ndim not in [2, 3]:
            raise ValueError("ImageColorGenerator needs an image with ndim 2 or"
                         " 3, got %d" % image.ndim)
        elif image.ndim == 3 and image.shape[2] not in [3, 4]:
            raise ValueError("A color image needs to have 3 or 4 channels, got %d"
                         % image.shape[2])

        colors = Counter([tuple(colors) for i in image for colors in i]).most_common()
        if max_colors != np.inf:
            self.ucolors += colors[:max_colors]
        else:
            self.ucolors += colors
        return self

    def shuffle_colors(self, seed = 42):
        """Shuffle the colors of the palette

        Parameters
        ----------
        seed : A custom seed.

        Returns
        -------
        self : The object to allow chaining.
        """
        random.seed(seed)
        random.shuffle(self.ucolors)
        return self

    def __call__(self, word, font_size, font_path, position, orientation, **kwargs):
        """Generate a color for a given word using a fixed image."""
        # get the font to get the box size

        color_txt = "rgb(%d, %d, %d)" % self.ucolors[np.mod(self.color_index, len(self.ucolors))][0][0:3]
        self.color_index += 1
        return color_txt

# -*- coding: utf-8 -*-
"""Command-line tool interface to generate word clouds.
"""
from __future__ import absolute_import

import sys
import textwrap

if __name__ == '__main__':  # pragma: no cover
    sys.exit(textwrap.dedent(
        """
        To execute the CLI, instead consider running:

          wordcloud_cli --help

        or

          python -m wordcloud --help
        """))

import io
import re
import argparse
import wordcloud as wc
import numpy as np
from PIL import Image

from . import __version__


class FileType(object):
    """Factory for creating file object types.

    Port from argparse so we can support unicode file reading in Python2

    Instances of FileType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - mode -- A string indicating how the file is to be opened. Accepts the
            same values as the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.

    """

    def __init__(self, mode='r', bufsize=-1):
        self._mode = mode
        self._bufsize = bufsize

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        if string == '-':
            if 'r' in self._mode:
                return sys.stdin
            elif 'w' in self._mode:
                return sys.stdout.buffer if 'b' in self._mode else sys.stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            encoding = None if 'b' in self._mode else "UTF-8"
            return io.open(string, self._mode, self._bufsize, encoding=encoding)
        except IOError as e:
            message = "can't open '%s': %s"
            raise argparse.ArgumentTypeError(message % (string, e))

    def __repr__(self):
        args = self._mode, self._bufsize
        args_str = ', '.join(repr(arg) for arg in args if arg != -1)
        return '%s(%s)' % (type(self).__name__, args_str)


class RegExpAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(RegExpAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            re.compile(values)
        except re.error as e:
            raise argparse.ArgumentError(self, 'Invalid regular expression: ' + str(e))
        setattr(namespace, self.dest, values)


def main(args, text, imagefile):
    wordcloud = wc.WordCloud(**args)
    wordcloud.generate(text)
    image = wordcloud.to_image()

    with imagefile:
        image.save(imagefile, format='png', optimize=True)


def make_parser():
    description = 'A simple command line interface for wordcloud module.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--text', metavar='file', type=FileType(), default='-',
        help='specify file of words to build the word cloud (default: stdin)')
    parser.add_argument(
        '--regexp', metavar='regexp', default=None, action=RegExpAction,
        help='override the regular expression defining what constitutes a word')
    parser.add_argument(
        '--stopwords', metavar='file', type=FileType(),
        help='specify file of stopwords (containing one word per line)'
             ' to remove from the given text after parsing')
    parser.add_argument(
        '--imagefile', metavar='file', type=FileType('wb'),
        default='-',
        help='file the completed PNG image should be written to'
             ' (default: stdout)')
    parser.add_argument(
        '--fontfile', metavar='path', dest='font_path',
        help='path to font file you wish to use (default: DroidSansMono)')
    parser.add_argument(
        '--mask', metavar='file', type=argparse.FileType('rb'),
        help='mask to use for the image form')
    parser.add_argument(
        '--colormask', metavar='file', type=argparse.FileType('rb'),
        help='color mask to use for image coloring')
    parser.add_argument(
        '--contour_width', metavar='width', default=0, type=float,
        dest='contour_width',
        help='if greater than 0, draw mask contour (default: 0)')
    parser.add_argument(
        '--contour_color', metavar='color', default='black', type=str,
        dest='contour_color',
        help='use given color as mask contour color -'
             ' accepts any value from PIL.ImageColor.getcolor')
    parser.add_argument(
        '--relative_scaling', type=float, default=0,
        metavar='rs', help=' scaling of words by frequency (0 - 1)')
    parser.add_argument(
        '--margin', type=int, default=2,
        metavar='width', help='spacing to leave around words')
    parser.add_argument(
        '--width', type=int, default=400,
        metavar='width', help='define output image width')
    parser.add_argument(
        '--height', type=int, default=200,
        metavar='height', help='define output image height')
    parser.add_argument(
        '--color', metavar='color',
        help='use given color as coloring for the image -'
             ' accepts any value from PIL.ImageColor.getcolor')
    parser.add_argument(
        '--background', metavar='color', default='black', type=str,
        dest='background_color',
        help='use given color as background color for the image -'
             ' accepts any value from PIL.ImageColor.getcolor')
    parser.add_argument(
        '--no_collocations', action='store_false', dest='collocations',
        help='do not add collocations (bigrams) to word cloud '
             '(default: add unigrams and bigrams)')
    parser.add_argument(
        '--include_numbers',
        action='store_true',
        dest='include_numbers',
        help='include numbers in wordcloud?')
    parser.add_argument(
        '--min_word_length',
        type=int,
        default=0,
        metavar='min_word_length',
        dest='min_word_length',
        help='only include words with more than X letters')
    parser.add_argument(
        '--prefer_horizontal',
        type=float, default=.9, metavar='ratio',
        help='ratio of times to try horizontal fitting as opposed to vertical')
    parser.add_argument(
        '--scale',
        type=float, default=1, metavar='scale',
        help='scaling between computation and drawing')
    parser.add_argument(
        '--colormap',
        type=str, default='viridis', metavar='map',
        help='matplotlib colormap name')
    parser.add_argument(
        '--mode',
        type=str, default='RGB', metavar='mode',
        help='use RGB or RGBA for transparent background')
    parser.add_argument(
        '--max_words',
        type=int, default=200, metavar='N',
        help='maximum number of words')
    parser.add_argument(
        '--min_font_size',
        type=int, default=4, metavar='size',
        help='smallest font size to use')
    parser.add_argument(
        '--max_font_size',
        type=int, default=None, metavar='size',
        help='maximum font size for the largest word')
    parser.add_argument(
        '--font_step',
        type=int, default=1, metavar='step',
        help='step size for the font')
    parser.add_argument(
        '--random_state',
        type=int, default=None, metavar='seed',
        help='random seed')
    parser.add_argument(
        '--no_normalize_plurals',
        action='store_false',
        dest='normalize_plurals',
        help='whether to remove trailing \'s\' from words')
    parser.add_argument(
        '--repeat',
        action='store_true',
        dest='repeat',
        help='whether to repeat words and phrases')
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    return parser


def parse_args(arguments):
    # prog = 'python wordcloud_cli.py'
    parser = make_parser()
    args = parser.parse_args(arguments)

    if args.colormask and args.color:
        raise ValueError('specify either a color mask or a color function')

    args = vars(args)

    with args.pop('text') as f:
        text = f.read()

    if args['stopwords']:
        with args.pop('stopwords') as f:
            args['stopwords'] = set(map(lambda l: l.strip(), f.readlines()))

    if args['mask']:
        mask = args.pop('mask')
        args['mask'] = np.array(Image.open(mask))

    color_func = wc.random_color_func
    colormask = args.pop('colormask')
    color = args.pop('color')
    if colormask:
        image = np.array(Image.open(colormask))
        color_func = wc.ImageColorGenerator(image)
    if color:
        color_func = wc.get_single_color_func(color)
    args['color_func'] = color_func

    imagefile = args.pop('imagefile')

    return args, text, imagefile

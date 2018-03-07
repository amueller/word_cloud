#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Command-line tool to generate word clouds
Usage::
    $ cat word.txt | wordcloud_cli.py

    $ wordcloud_cli.py --text=words.txt --stopwords=stopwords.txt
"""
from __future__ import absolute_import

import sys
import io
import re
import argparse
import wordcloud as wc
import numpy as np
from PIL import Image

from wordcloud import __version__


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
                return sys.stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            return io.open(string, self._mode, self._bufsize, encoding="UTF-8")
        except IOError as e:
            message = "can't open '%s': %s"
            raise argparse.ArgumentTypeError(message % (string, e))

    def __repr__(self):
        args = self._mode, self._bufsize
        args_str = ', '.join(repr(arg) for arg in args if arg != -1)
        return '%s(%s)' % (type(self).__name__, args_str)


class RegExpAction(argparse.Action):
     def __init__(self, option_strings, dest, **kwargs):
         for option in option_strings:
             try:
                 re.compile(option)
             except re.error as e:
                 raise argparse.ArgumentError('Invalid regular expression: ' + str(e))
         super(RegExpAction, self).__init__(option_strings, dest, **kwargs)

     def __call__(self, parser, namespace, values, option_string=None):
         setattr(namespace, self.dest, values)


def main(args, text, imagefile):
    wordcloud = wc.WordCloud(**args)
    wordcloud.generate(text)
    image = wordcloud.to_image()

    with imagefile:
        image.save(imagefile, format='png', optimize=True)


def parse_args(arguments):
    # prog = 'python wordcloud_cli.py'
    description = ('A simple command line interface for wordcloud module.')
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
        '--imagefile', metavar='file', type=argparse.FileType('wb'),
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
    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args(arguments)

    if args.colormask and args.color:
        raise ValueError('specify either a color mask or a color function')

    args = vars(args)

    with args.pop('text') as f:
        text = f.read()

    if args['stopwords']:
        with args.pop('stopwords') as f:
            args['stopwords'] = set(map(str.strip, f.readlines()))

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

if __name__ == '__main__':
    main(*parse_args(sys.argv[1:]))

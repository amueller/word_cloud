#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Command-line tool to generate word clouds
Usage::
    $ cat word.txt | wordcloud_cli.py

    $ wordcloud_cli.py --text=words.txt --stopwords=stopwords.txt
"""
import argparse
import wordcloud as wc
import numpy as np
import sys
from PIL import Image

def main(args):
    wordcloud = wc.WordCloud(stopwords=args.stopwords, mask=args.mask,
        width=args.width, height=args.height, font_path=args.font_path,
        margin=args.margin, relative_scaling=args.relative_scaling,
        color_func=args.color_func, background_color=args.background_color).generate(args.text)
    image = wordcloud.to_image()

    with args.imagefile:
        out = args.imagefile if sys.version < '3' else args.imagefile.buffer
        image.save(out, format='png')

def parse_args(arguments):
    prog = 'python wordcloud_cli.py'
    description = ('A simple command line interface for wordcloud module.')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--text', metavar='file', type=argparse.FileType(), default='-',
        help='specify file of words to build the word cloud (default: stdin)')
    parser.add_argument('--stopwords', metavar='file', type=argparse.FileType(),
        help='specify file of stopwords (containing one word per line) to remove from the given text after parsing')
    parser.add_argument('--imagefile', metavar='file', type=argparse.FileType('w'), default='-',
        help='file the completed PNG image should be written to (default: stdout)')
    parser.add_argument('--fontfile', metavar='path', dest='font_path',
        help='path to font file you wish to use (default: DroidSansMono)')
    parser.add_argument('--mask', metavar='file', type=argparse.FileType(),
        help='mask to use for the image form')
    parser.add_argument('--colormask', metavar='file', type=argparse.FileType(),
        help='color mask to use for image coloring')
    parser.add_argument('--relative_scaling', type=float, default=0,
        metavar='rs', help=' scaling of words by frequency (0 - 1)')
    parser.add_argument('--margin', type=int, default=2,
        metavar='width', help='spacing to leave around words')
    parser.add_argument('--width', type=int, default=400,
        metavar='width', help='define output image width')
    parser.add_argument('--height', type=int, default=200,
        metavar='height', help='define output image height')
    parser.add_argument('--color', metavar='color',
        help='use given color as coloring for the image - accepts any value from PIL.ImageColor.getcolor')
    parser.add_argument('--background', metavar='color', default='black', type=str, dest='background_color',
        help='use given color as background color for the image - accepts any value from PIL.ImageColor.getcolor')
    args = parser.parse_args(arguments)

    if args.colormask and args.color:
        raise ValueError('specify either a color mask or a color function')

    with args.text:
        args.text = args.text.read()

    if args.stopwords:
        with args.stopwords:
            args.stopwords = set(map(str.strip, args.stopwords.readlines()))

    if args.mask:
        args.mask = np.array(Image.open(args.mask))

    color_func = wc.random_color_func
    if args.colormask:
        image = np.array(Image.open(args.colormask))
        color_func = wc.ImageColorGenerator(image)

    if args.color:
        color_func = wc.get_single_color_func(args.color)

    args.color_func = color_func
    return args

if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))

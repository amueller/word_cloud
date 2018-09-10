# -*- coding: utf-8 -*-
"""Command line tool to generate word clouds

The name ``__main__.py`` is important as it enables execution
of the module using ``python -m wordcloud`` syntax.

Usage:

* using ``wordcloud_cli`` executable::

    $ cat word.txt | wordcloud_cli

    $ wordcloud_cli --text=words.txt --stopwords=stopwords.txt

* using ``wordcloud`` module::

    $ cat word.txt | python -m wordcloud

    $ python -m wordcloud --text=words.txt --stopwords=stopwords.txt
"""

import sys

from .wordcloud_cli import main as wordcloud_cli_main
from .wordcloud_cli import parse_args as wordcloud_cli_parse_args


def main():
    """The main entry point to wordcloud_cli``.

    This is installed as the script entry point.
    """
    wordcloud_cli_main(*wordcloud_cli_parse_args(sys.argv[1:]))


if __name__ == '__main__':  # pragma: no cover
    main()

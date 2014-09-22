from wordcloud import WordCloud
import numpy as np
from nose.tools import assert_equal
from numpy.testing import assert_array_equal

THIS = """The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
"""


def test_default():
    wc = WordCloud(max_words=50)
    wc.generate(THIS)

    # check for proper word extraction
    assert_equal(len(wc.words_), wc.max_words)

    # check that we got enough words
    assert_equal(len(wc.layout_), wc.max_words)

    # check image export
    wc_image = wc.to_image()
    assert_equal(wc_image.size, (wc.width, wc.height))

    # check that numpy conversion works
    wc_array = np.array(wc)
    assert_array_equal(wc_array, wc.to_array())

    # check size
    assert_equal(wc_array.shape, (wc.height, wc.width, 3))


def check_errors():
    pass


def test_recolor():
    pass


def test_mask():
    pass

from wordcloud import WordCloud, get_single_color_func, ImageColorGenerator
import numpy as np
from random import Random
from nose.tools import (assert_equal, assert_greater, assert_true, assert_false,
                        assert_raises, assert_in, assert_not_in)
try:
    from nose.tools import assert_raises_regex
except ImportError:
    from nose.tools import assert_raises_regexp as assert_raises_regex
from numpy.testing import assert_array_equal
from PIL import Image

from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')

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


def test_collocations():
    wc = WordCloud(collocations=False, stopwords=[])
    wc.generate(THIS)

    wc2 = WordCloud(collocations=True, stopwords=[])
    wc2.generate(THIS)

    assert_in("is better", wc2.words_)
    assert_not_in("is better", wc.words_)
    assert_not_in("way may", wc2.words_)


def test_plurals_numbers():
    text = THIS + "\n" + "1 idea 2 ideas three ideas although many Ideas"
    wc = WordCloud(stopwords=[]).generate(text)
    # not capitalized usually
    assert_not_in("Ideas", wc.words_)
    # plural removed
    assert_not_in("ideas", wc.words_)
    # usually capitalized
    assert_not_in("although", wc.words_)
    assert_in("idea", wc.words_)
    assert_in("Although", wc.words_)
    assert_in("better than", wc.words_)


def test_multiple_s():
    text = 'flo flos floss flosss'
    wc = WordCloud(stopwords=[]).generate(text)
    assert_in("flo", wc.words_)
    assert_not_in("flos", wc.words_)
    assert_in("floss", wc.words_)
    assert_in("flosss", wc.words_)
    # not normalizing means that the one with just one s is kept
    wc = WordCloud(stopwords=[], normalize_plurals=False).generate(text)
    assert_in("flo", wc.words_)
    assert_in("flos", wc.words_)
    assert_in("floss", wc.words_)
    assert_in("flosss", wc.words_)


def test_empty_text():
    # test originally empty text raises an exception
    wc = WordCloud(stopwords=[])
    assert_raises(ValueError, wc.generate, '')

    # test empty-after-filtering text raises an exception
    wc = WordCloud(stopwords=['a', 'b'])
    assert_raises(ValueError, wc.generate, 'a b a')


def test_default():
    # test that default word cloud creation and conversions work
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


def test_stopwords_lowercasing():
    # test that capitalized stopwords work.
    wc = WordCloud(stopwords=["Beautiful"])
    processed = wc.process_text(THIS)
    words = [count[0] for count in processed]
    assert_true("Beautiful" not in words)


def test_writing_to_file():
    wc = WordCloud()
    wc.generate(THIS)
    # check writing to file
    f = NamedTemporaryFile(suffix=".png")
    filename = f.name
    wc.to_file(filename)
    loaded_image = Image.open(filename)
    assert_equal(loaded_image.size, (wc.width, wc.height))


def test_check_errors():
    wc = WordCloud()
    assert_raises(NotImplementedError, wc.to_html)

    try:
        np.array(wc)
        raise AssertionError("np.array(wc) didn't raise")
    except ValueError as e:
        assert_true("call generate" in str(e))

    try:
        wc.recolor()
        raise AssertionError("wc.recolor didn't raise")
    except ValueError as e:
        assert_true("call generate" in str(e))


def test_recolor():
    wc = WordCloud(max_words=50, colormap="jet")
    wc.generate(THIS)
    array_before = wc.to_array()
    wc.recolor()
    array_after = wc.to_array()
    # check that the same places are filled
    assert_array_equal(array_before.sum(axis=-1) != 0,
                       array_after.sum(axis=-1) != 0)
    # check that they are not the same
    assert_greater(np.abs(array_before - array_after).sum(), 10000)

    # check that recoloring is deterministic
    wc.recolor(random_state=10)
    wc_again = wc.to_array()
    assert_array_equal(wc_again, wc.recolor(random_state=10))


def test_random_state():
    # check that random state makes everything deterministic
    wc = WordCloud(random_state=0)
    wc2 = WordCloud(random_state=0)
    wc.generate(THIS)
    wc2.generate(THIS)
    assert_array_equal(wc, wc2)


def test_mask():
    # test masks

    # check that using an empty mask is equivalent to not using a mask
    wc = WordCloud(random_state=42)
    wc.generate(THIS)
    mask = np.zeros(np.array(wc).shape[:2], dtype=np.int)
    wc_mask = WordCloud(mask=mask, random_state=42)
    wc_mask.generate(THIS)
    assert_array_equal(wc, wc_mask)

    # use actual nonzero mask
    mask = np.zeros((234, 456), dtype=np.int)
    mask[100:150, 300:400] = 255

    wc = WordCloud(mask=mask)
    wc.generate(THIS)
    wc_array = np.array(wc)
    assert_equal(mask.shape, wc_array.shape[:2])
    assert_array_equal(wc_array[mask != 0], 0)
    assert_greater(wc_array[mask == 0].sum(), 10000)


def test_single_color_func():
    # test single color function for different color formats
    random = Random(42)

    red_function = get_single_color_func('red')
    assert_equal(red_function(random_state=random), 'rgb(181, 0, 0)')

    hex_function = get_single_color_func('#00b4d2')
    assert_equal(hex_function(random_state=random), 'rgb(0, 48, 56)')

    rgb_function = get_single_color_func('rgb(0,255,0)')
    assert_equal(rgb_function(random_state=random), 'rgb(0, 107, 0)')

    rgb_perc_fun = get_single_color_func('rgb(80%,60%,40%)')
    assert_equal(rgb_perc_fun(random_state=random), 'rgb(97, 72, 48)')

    hsl_function = get_single_color_func('hsl(0,100%,50%)')
    assert_equal(hsl_function(random_state=random), 'rgb(201, 0, 0)')


def test_single_color_func_grey():
    # grey is special as it's a corner case
    random = Random(42)

    red_function = get_single_color_func('darkgrey')
    assert_equal(red_function(random_state=random), 'rgb(181, 181, 181)')
    assert_equal(red_function(random_state=random), 'rgb(56, 56, 56)')


def test_process_text():
    # test that process function returns a dict
    wc = WordCloud(max_words=50)
    result = wc.process_text(THIS)

    # check for proper return type
    assert_true(isinstance(result, dict))


def test_process_text_regexp_parameter():
    # test that word processing is influenced by `regexp`
    wc = WordCloud(max_words=50, regexp=r'\w{5}')
    words = wc.process_text(THIS)

    assert_false('than' in words)


def test_generate_from_frequencies():
    # test that generate_from_frequencies() takes input argument dicts
    wc = WordCloud(max_words=50)
    words = wc.process_text(THIS)
    result = wc.generate_from_frequencies(words)

    assert_true(isinstance(result, WordCloud))


def test_relative_scaling_zero():
    # non-regression test for non-integer font size
    wc = WordCloud(relative_scaling=0)
    wc.generate(THIS)


def test_unicode_stopwords():
    wc_unicode = WordCloud(stopwords=[u'Beautiful'])
    try:
        words_unicode = wc_unicode.process_text(unicode(THIS))
    except NameError:  # PY3
        words_unicode = wc_unicode.process_text(THIS)

    wc_str = WordCloud(stopwords=['Beautiful'])
    words_str = wc_str.process_text(str(THIS))

    assert_true(words_unicode == words_str)

    
def test_recolor_too_small():
    # check exception is raised when image is too small
    colouring = np.array(Image.new('RGB', size=(20, 20)))
    wc = WordCloud(width=30, height=30).generate(THIS)
    image_colors = ImageColorGenerator(colouring)
    assert_raises_regex(ValueError, 'ImageColorGenerator is smaller than the canvas',
                        wc.recolor, color_func=image_colors)


def test_recolor_too_small_set_default():
    # check no exception is raised when default colour is used
    colouring = np.array(Image.new('RGB', size=(20, 20)))
    wc = WordCloud(max_words=50, width=30, height=30).generate(THIS)
    image_colors = ImageColorGenerator(colouring, default_color=(0, 0, 0))
    wc.recolor(color_func=image_colors)
    
    
def test_small_canvas():
    # check font size fallback works on small canvas
    WordCloud(max_words=50, width=20, height=20).generate(THIS)
    
    
def test_tiny_canvas():
    # check exception if canvas too small for fallback
    w = WordCloud(max_words=50, width=1, height=1)
    assert_raises_regex(ValueError, 'canvas size is too small',
                        w.generate, THIS)

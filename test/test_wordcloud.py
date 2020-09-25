from wordcloud import WordCloud, get_single_color_func, ImageColorGenerator

import numpy as np
import pytest

from random import Random
from numpy.testing import assert_array_equal
from PIL import Image
import xml.etree.ElementTree as ET

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

3 . 14 15 92 65 35   89 79 32 38 46   26 433
    83 27 95 02 88   41 97 16 93 99   37 510
    58 20 97 49 44   59 23 07 81 64   06 286
    20 89 98 62 80   34 82 53 42 11   70 679
    82 14 80 86 51   32 82 30 66 47   09 384
    46 09 55 05 82   23 17 25 35 94   08 128
"""

STOPWORDED_COLLOCATIONS = """
thank you very much
thank you very much
thank you very much
thanks
"""

STOPWORDED_COLLOCATIONS_UPPERCASE = """
Thank you very much
Thank you very much
Thank you very much
thank you very much
hi There
Hi there
Hi There
thanks
"""

SMALL_CANVAS = """
better late than never someone will say
"""


def test_collocations():
    wc = WordCloud(collocations=False, stopwords=set())
    wc.generate(THIS)

    wc2 = WordCloud(collocations=True, stopwords=set())
    wc2.generate(THIS)

    assert "is better" in wc2.words_
    assert "is better" not in wc.words_
    assert "way may" not in wc2.words_


def test_collocation_stopwords():
    wc = WordCloud(collocations=True, stopwords={"you", "very"}, collocation_threshold=9)
    wc.generate(STOPWORDED_COLLOCATIONS)

    assert "thank you" not in wc.words_
    assert "very much" not in wc.words_
    assert "thank" in wc.words_
    # a bigram of all stopwords will be removed
    assert "you very" not in wc.words_


def test_collocation_stopwords_uppercase():
    wc = WordCloud(collocations=True, stopwords={"thank", "hi", "there"}, collocation_threshold=9)
    wc.generate(STOPWORDED_COLLOCATIONS_UPPERCASE)

    assert "Thank you" not in wc.words_
    assert "thank you" not in wc.words_
    assert "Thank" not in wc.words_
    # a bigram of all stopwords will be removed
    assert "hi There" not in wc.words_
    assert "Hi there" not in wc.words_
    assert "Hi There" not in wc.words_


def test_plurals_numbers():
    text = THIS + "\n" + "1 idea 2 ideas three ideas although many Ideas"
    wc = WordCloud(stopwords=[]).generate(text)
    # not capitalized usually
    assert "Ideas" not in wc.words_
    # plural removed
    assert "ideas" not in wc.words_
    # usually capitalized
    assert "although" not in wc.words_
    assert "idea" in wc.words_
    assert "Although" in wc.words_
    assert "better than" in wc.words_


def test_multiple_s():
    text = 'flo flos floss flosss'
    wc = WordCloud(stopwords=[]).generate(text)
    assert "flo" in wc.words_
    assert "flos" not in wc.words_
    assert "floss" in wc.words_
    assert "flosss" in wc.words_
    # not normalizing means that the one with just one s is kept
    wc = WordCloud(stopwords=[], normalize_plurals=False).generate(text)
    assert "flo" in wc.words_
    assert "flos" in wc.words_
    assert "floss" in wc.words_
    assert "flosss" in wc.words_


def test_empty_text():
    # test originally empty text raises an exception
    wc = WordCloud(stopwords=[])
    with pytest.raises(ValueError):
        wc.generate('')

    # test empty-after-filtering text raises an exception
    wc = WordCloud(stopwords=['a', 'b'])
    with pytest.raises(ValueError):
        wc.generate('a b a')


def test_default():
    # test that default word cloud creation and conversions work
    wc = WordCloud(max_words=50)
    wc.generate(THIS)

    # check for proper word extraction
    assert len(wc.words_) == wc.max_words

    # check that we got enough words
    assert len(wc.layout_) == wc.max_words

    # check image export
    wc_image = wc.to_image()
    assert wc_image.size == (wc.width, wc.height)

    # check that numpy conversion works
    wc_array = np.array(wc)
    assert_array_equal(wc_array, wc.to_array())

    # check size
    assert wc_array.shape == (wc.height, wc.width, 3)


def test_stopwords_lowercasing():
    # test that capitalized stopwords work.
    wc = WordCloud(stopwords=["Beautiful"])
    processed = wc.process_text(THIS)
    words = [count[0] for count in processed]
    assert "Beautiful" not in words


def test_writing_to_file(tmpdir):
    wc = WordCloud()
    wc.generate(THIS)

    # check writing to file
    filename = str(tmpdir.join("word_cloud.png"))
    wc.to_file(filename)
    loaded_image = Image.open(filename)
    assert loaded_image.size == (wc.width, wc.height)


def test_check_errors():
    wc = WordCloud()
    with pytest.raises(NotImplementedError):
        wc.to_html()

    try:
        np.array(wc)
        raise AssertionError("np.array(wc) didn't raise")
    except ValueError as e:
        assert "call generate" in str(e)

    try:
        wc.recolor()
        raise AssertionError("wc.recolor didn't raise")
    except ValueError as e:
        assert "call generate" in str(e)


def test_svg_syntax():
    wc = WordCloud()
    wc.generate(THIS)
    svg = wc.to_svg()
    ET.fromstring(svg)


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
    assert np.abs(array_before - array_after).sum() > 10000

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
    assert mask.shape == wc_array.shape[:2]
    assert_array_equal(wc_array[mask != 0], 0)
    assert wc_array[mask == 0].sum() > 10000


def test_mask_contour():
    # test mask contour is created, learn more at:
    # https://github.com/amueller/word_cloud/pull/348#issuecomment-370883873
    mask = np.zeros((234, 456), dtype=np.int)
    mask[100:150, 300:400] = 255

    sm = WordCloud(mask=mask, contour_width=1, contour_color='blue')
    sm.generate(THIS)
    sm_array = np.array(sm)
    sm_total = sm_array[100:150, 300:400].sum()

    lg = WordCloud(mask=mask, contour_width=20, contour_color='blue')
    lg.generate(THIS)
    lg_array = np.array(lg)
    lg_total = lg_array[100:150, 300:400].sum()

    sc = WordCloud(mask=mask, contour_width=1, scale=2, contour_color='blue')
    sc.generate(THIS)
    sc_array = np.array(sc)
    sc_total = sc_array[100:150, 300:400].sum()

    # test `contour_width`
    assert lg_total > sm_total

    # test contour varies with `scale`
    assert sc_total > sm_total

    # test `contour_color`
    assert all(sm_array[100, 300] == [0, 0, 255])


def test_single_color_func():
    # test single color function for different color formats
    random = Random(42)

    red_function = get_single_color_func('red')
    assert red_function(random_state=random) == 'rgb(181, 0, 0)'

    hex_function = get_single_color_func('#00b4d2')
    assert hex_function(random_state=random) == 'rgb(0, 48, 56)'

    rgb_function = get_single_color_func('rgb(0,255,0)')
    assert rgb_function(random_state=random) == 'rgb(0, 107, 0)'

    rgb_perc_fun = get_single_color_func('rgb(80%,60%,40%)')
    assert rgb_perc_fun(random_state=random) == 'rgb(97, 72, 48)'

    hsl_function = get_single_color_func('hsl(0,100%,50%)')
    assert hsl_function(random_state=random) == 'rgb(201, 0, 0)'


def test_single_color_func_grey():
    # grey is special as it's a corner case
    random = Random(42)

    red_function = get_single_color_func('darkgrey')
    assert red_function(random_state=random) == 'rgb(181, 181, 181)'
    assert red_function(random_state=random) == 'rgb(56, 56, 56)'


def test_process_text():
    # test that process function returns a dict
    wc = WordCloud(max_words=50)
    result = wc.process_text(THIS)

    # check for proper return type
    assert isinstance(result, dict)


def test_process_text_default_patterns():
    wc = WordCloud(stopwords=set(), include_numbers=True, min_word_length=2)
    words = wc.process_text(THIS)

    wc2 = WordCloud(stopwords=set(), include_numbers=True, min_word_length=1)
    words2 = wc2.process_text(THIS)

    assert "a" not in words
    assert "3" not in words

    assert "a" in words2
    assert "3" in words2


def test_process_text_regexp_parameter():
    # test that word processing is influenced by `regexp`
    wc = WordCloud(max_words=50, regexp=r'\w{5}')
    words = wc.process_text(THIS)

    assert 'than' not in words


def test_generate_from_frequencies():
    # test that generate_from_frequencies() takes input argument dicts
    wc = WordCloud(max_words=50)
    words = wc.process_text(THIS)
    result = wc.generate_from_frequencies(words)

    assert isinstance(result, WordCloud)


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

    assert words_unicode == words_str


def test_include_numbers():
    wc_numbers = WordCloud(include_numbers=True)
    wc = wc_numbers.process_text(THIS)

    assert '14' in wc.keys()


def test_min_word_length():
    wc_numbers = WordCloud(min_word_length=5)
    wc = wc_numbers.process_text(THIS)
    word_lengths = [len(word) for word in wc.keys()]

    assert min(word_lengths) == 5


def test_recolor_too_small():
    # check exception is raised when image is too small
    colouring = np.array(Image.new('RGB', size=(20, 20)))
    wc = WordCloud(width=30, height=30, random_state=0, min_font_size=1).generate(THIS)
    image_colors = ImageColorGenerator(colouring)
    with pytest.raises(ValueError, match='ImageColorGenerator is smaller than the canvas'):
        wc.recolor(color_func=image_colors)


def test_recolor_too_small_set_default():
    # check no exception is raised when default colour is used
    colouring = np.array(Image.new('RGB', size=(20, 20)))
    wc = WordCloud(max_words=50, width=30, height=30, min_font_size=1).generate(THIS)
    image_colors = ImageColorGenerator(colouring, default_color=(0, 0, 0))
    wc.recolor(color_func=image_colors)


def test_small_canvas():
    # check font size fallback works on small canvas
    wc = WordCloud(max_words=50, width=21, height=21)
    wc.generate(SMALL_CANVAS)
    assert len(wc.layout_) > 0


def test_tiny_canvas():
    # check exception if canvas too small for fallback
    w = WordCloud(max_words=50, width=1, height=1)
    with pytest.raises(ValueError, match="Couldn't find space to draw"):
        w.generate(THIS)
    assert len(w.layout_) == 0


def test_coloring_black_works():
    # check that using black colors works.
    mask = np.zeros((50, 50, 3))
    image_colors = ImageColorGenerator(mask)
    wc = WordCloud(width=50, height=50, random_state=42,
                   color_func=image_colors, min_font_size=1)
    wc.generate(THIS)


def test_repeat():
    short_text = "Some short text"
    wc = WordCloud(stopwords=[]).generate(short_text)
    assert len(wc.layout_) == 3
    wc = WordCloud(max_words=50, stopwords=[], repeat=True).generate(short_text)
    # multiple of word count larger than max_words
    assert len(wc.layout_) == 51
    # relative scaling doesn't work well with repeat
    assert wc.relative_scaling == 0
    # all frequencies are 1
    assert len(wc.words_) == 3
    assert_array_equal(list(wc.words_.values()), 1)
    frequencies = [w[0][1] for w in wc.layout_]
    assert_array_equal(frequencies, 1)
    repetition_text = "Some short text with text"
    wc = WordCloud(max_words=52, stopwords=[], repeat=True)
    wc.generate(repetition_text)
    assert len(wc.words_) == 4
    # normalized frequencies
    assert wc.words_['text'] == 1
    assert wc.words_['with'] == .5
    assert len(wc.layout_), wc.max_words
    frequencies = [w[0][1] for w in wc.layout_]
    # check that frequencies are sorted
    assert np.all(np.diff(frequencies) <= 0)


def test_zero_frequencies():

    word_cloud = WordCloud()

    word_cloud.generate_from_frequencies({'test': 1, 'test1': 0, 'test2': 0})
    assert len(word_cloud.layout_) == 1
    assert word_cloud.layout_[0][0][0] == 'test'


def test_plural_stopwords():
    x = '''was was was was was was was was was was was was was was was
    wa
    hello hello hello hello hello hello hello hello
    goodbye good bye maybe yes no'''
    w = WordCloud().generate(x)
    assert w.words_['wa'] < 1

    w = WordCloud(collocations=False).generate(x)
    assert w.words_['wa'] < 1

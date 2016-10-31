#!/usr/bin/env python
"""
Colored by Group Example
===============
Generating a word cloud that assigns colors to words based on
a predefined mapping from colors to words
"""

from wordcloud import (WordCloud, get_single_color_func)
import matplotlib.pyplot as plt


def get_grouped_color_func(colors_to_words, default_color):
    """Create a color function which assigns colors to certain words
       based on the color to words mapping

       Parameters
       ----------
       colors_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from colors_to_words.
    """
    color_func_to_words = [(get_single_color_func(color), set(words))
                           for (color, words) in colors_to_words.items()]

    default_color_func = get_single_color_func(default_color)


    def grouped_color_func(word=None, font_size=None, position=None,
                             orientation=None, font_path=None, random_state=None, **kwargs):
        try:
            color_func = next(color_func
                              for (color_func, words) in color_func_to_words
                              if word in words)
        except StopIteration:
            color_func = default_color_func

        return color_func(word, font_size, position,
                          orientation, font_path, random_state, **kwargs)

    return grouped_color_func


text = """The Zen of Python, by Tim Peters
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
Namespaces are one honking great idea -- let's do more of those!"""

# Since the text is small collocations are turned off and text is lower-cased
wc = WordCloud(collocations=False).generate(text.lower())

colors_to_words = {
    # words below will be colored with a green single color function
    '#00ff00': ['beautiful', 'explicit', 'simple', 'sparse',
                'readability', 'rules', 'practicality',
                'explicitly', 'one', 'now', 'easy', 'obvious', 'better'],
    # will be colored with a red single color function
    'red': ['ugly', 'implicit', 'complex', 'complicated', 'nested',
            'dense', 'special', 'errors', 'silently', 'ambiguity',
            'guess', 'hard']
}

# Words that are not in any of the colors_to_words values
# will be colored with a grey single color function
default_color = 'grey'

# Create a color function
grouped_color_func = get_grouped_color_func(colors_to_words, default_color)

# Apply our color function
wc.recolor(color_func=grouped_color_func)

# Plot
plt.figure()
plt.imshow(wc)
plt.axis("off")
plt.show()

"""
Using number frequency parameter
===============

"""

from os import path, getcwd

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else getcwd()
# read text
text = open(path.join(d, 'numbers.txt'), encoding='utf-8')
text = text.read()

# create & generate cloud
wc = WordCloud(background_color="white", max_words=1000, include_numbers=True).generate(text)
wc.to_file(path.join(d, 'number_freq'))

plt.imshow(wc)
plt.axis("off")
plt.show()
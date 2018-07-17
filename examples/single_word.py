"""
Single Word
===========

Make a word cloud with a single word that's repeated.
"""

import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

text = "square"

x, y = np.ogrid[:300, :300]

mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
mask = 255 * mask.astype(int)


wc = WordCloud(repeat=True, mask=mask).generate(text)

plt.imshow(wc)
plt.figure()
plt.imshow(mask)
plt.show()

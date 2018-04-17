# -*- coding: utf-8 -*-

from wordcloud import WordCloud
import matplotlib.pyplot as plt

text = '''
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
明了 is 胜于 than implicit.
简洁 is 胜于 than complex.
复杂 is 胜于 than complicated.
扁平 is 胜于 优美的代码 than nested.
间隔 is 胜于 than dense.
可读性 counts.
Special cases 优美的代码 aren't special enough to break the rules.
Although practicality beats purity.
Errors should 优美的代码 never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- 优美的代码 and preferably only one --obvious way to do it.
Although that way may not 优美的代码 be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
'''

# the font from github: https://github.com/adobe-fonts
font = './fonts/AdobeFonts/SourceHanSerifSC-Regular.otf'
wc = WordCloud(collocations=False, font_path=font, width=1000, height=1000, margin=2).generate(text.lower())

plt.imshow(wc)
plt.axis("off")
plt.show()

wc.to_file('showChinese.png')



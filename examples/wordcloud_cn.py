# - * - coding: utf - 8 -*-
"""
create wordcloud with chinese
=======================

Wordcloud is a very good tools, but if you want to create
Chinese wordcloud only wordcloud is not enough. The file
shows how to use wordcloud with Chinese. First, you need a
Chinese word segmentation library jieba, jieba is now the
most elegant the most popular Chinese word segmentation tool in python.
You can use 'PIP install jieba'. To install it. As you can see,
at the same time using wordcloud with jieba very convenient
"""

import jieba
from os import path
from scipy.misc import imread
import matplotlib.pyplot as plt
# jieba.load_userdict("txt\userdict.txt")
# add userdict by load_userdict()
from wordcloud import WordCloud, ImageColorGenerator,STOPWORDS

d = path.dirname(__file__)

stopwords_path = d + '/stopwords/CNENstopwords.txt'
font_path = d + '/Fonts/simkai.ttf'

# the path to save worldcloud
imgname1 = d + '/WordCloudDefautColors.png'
imgname2 = d + '/WordCloudColorsByImg.png'
# read the mask / color image taken from
back_coloring = imread(path.join(d, d + '/img/DragonRaja.jpg'))

# Read the whole text.
text = open(path.join(d, d + '/txt/DragonRaja.txt')).read()

# if you want use wordCloud,you need it
# add userdict by add_word()
userdict_list = ['路明非']
for word in userdict_list:
    jieba.add_word(word)

f_stop = open(stopwords_path,encoding='utf8')
try:
    f_stop_text = f_stop.read()
    f_stop_seg_list = f_stop_text.split('\n')
finally:
    f_stop.close()

stopwords = set(STOPWORDS)
for stopword in f_stop_seg_list:
    stopwords.add(stopword)

wc = WordCloud(font_path=font_path,background_color="white",max_words=2000,mask=back_coloring,
               max_font_size=100,random_state=42,width=1000, height=860, margin=2,)


wc.generate(' '.join(jieba.cut(text)))

# create coloring from image
image_colors_default = ImageColorGenerator(back_coloring)

plt.figure()
# recolor wordcloud and show
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

# save wordcloud
wc.to_file(path.join(d, imgname1))

# create coloring from image
image_colors_byImg = ImageColorGenerator(back_coloring)

# show
# we could also give color_func=image_colors directly in the constructor
plt.imshow(wc.recolor(color_func=image_colors_byImg), interpolation="bilinear")
plt.axis("off")
plt.figure()
plt.imshow(back_coloring, interpolation="bilinear")
plt.axis("off")
plt.show()

# save wordcloud
wc.to_file(path.join(d, imgname2))

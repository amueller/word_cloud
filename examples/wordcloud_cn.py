# - * - coding: utf - 8 -*-
"""
create wordcloud with chinese
=============================

Wordcloud is a very good tools, but if you want to create
Chinese wordcloud only wordcloud is not enough. The file
shows how to use wordcloud with Chinese. First, you need a
Chinese word segmentation library jieba or HanLp.You can
use 'PIP install jieba' or 'PIP install pyhanlp' or to
install it.But yhanlp provides a python interface for hanlp.
Hanlp is currently the best-performing open source Chinese
natural language processing class library, but because it is
implemented in Java, so we must use the jpype to call Java
classes.So we have to use "pip install jpype1" to install
it.As you can see,at the same time using wordcloud with
jieba or pyhanlp very convenient.While jieba is lighter,
hanlp requires more downloads, but is more powerful HanLP's
level of identity of named entity,word segmentation was
better than jieba,and has more ways to do it.You'll save
a lot of time when you use it.
"""
from os import path, getcwd
from scipy.misc import imread
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else getcwd()

stopwords_path = d + '/wc_cn/stopwords_cn_en.txt'
# Chinese fonts must be set
font_path = d + '/fonts/SourceHanSerif/SourceHanSerifK-Light.otf'

# the path to save worldcloud
imgname1 = d + '/wc_cn/LuXun.jpg'
imgname2 = d + '/wc_cn/LuXun_colored.jpg'
# read the mask / color image taken from
back_coloring = imread(path.join(d, d + '/wc_cn/LuXun_color.jpg'))

# Read the whole text.
text = open(path.join(d, d + '/wc_cn/CalltoArms.txt')).read()

# if you want use wordCloud,you need it add userdict
# If use HanLp,Maybe you don't need to use it
userdict_list = ['阿Ｑ', '孔乙己', '单四嫂子']

isUseJieba = True

# use HanLP
# You can use the stop word feature to improve performance, or disable it to increase speed
isUseStopwordsByHanLP = False


# The function for processing text with Jieba
def jieba_processing_txt(text):
    for word in userdict_list:
        jieba.add_word(word)

    mywordlist = []
    seg_list = jieba.cut(text, cut_all=False)
    liststr = "/ ".join(seg_list)

    with open(stopwords_path, encoding='utf-8') as f_stop:
        f_stop_text = f_stop.read()
        f_stop_seg_list = f_stop_text.splitlines()

    for myword in liststr.split('/'):
        if not (myword.strip() in f_stop_seg_list) and len(myword.strip()) > 1:
            mywordlist.append(myword)
    return ' '.join(mywordlist)


# The function for processing text with HaanLP
def pyhanlp_processing_txt(text, isUseStopwordsOfHanLP=True):
    CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")
    for word in userdict_list:
        CustomDictionary.add(word)

    mywordlist = []
    HanLP.Config.ShowTermNature = False
    CRFnewSegment = HanLP.newSegment("viterbi")

    fianlText = []
    if isUseStopwordsByHanLP == True:
        CoreStopWordDictionary = JClass("com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary")
        text_list = CRFnewSegment.seg(text)
        CoreStopWordDictionary.apply(text_list)
        fianlText = [i.word for i in text_list]
    else:
        fianlText = list(CRFnewSegment.segment(text))
    liststr = "/ ".join(fianlText)

    with open(stopwords_path, encoding='utf-8') as f_stop:
        f_stop_text = f_stop.read()
        f_stop_seg_list = f_stop_text.splitlines()

    for myword in liststr.split('/'):
        if not (myword.strip() in f_stop_seg_list) and len(myword.strip()) > 1:
            mywordlist.append(myword)
    return ' '.join(mywordlist)


result_text = ''
if isUseJieba:
    import jieba

    jieba.enable_parallel(4)
    # Setting up parallel processes :4 ,but unable to run on Windows
    # jieba.load_userdict("txt\userdict.txt")
    # add userdict by load_userdict()
    result_text = jieba_processing_txt(text)
else:
    from pyhanlp import *
    from jpype import JClass, startJVM, getDefaultJVMPath, isThreadAttachedToJVM, attachThreadToJVM

    result_text = pyhanlp_processing_txt(text, isUseStopwordsOfHanLP=True)

wc = WordCloud(font_path=font_path, background_color="white", max_words=2000, mask=back_coloring,
               max_font_size=100, random_state=42, width=1000, height=860, margin=2, )

wc.generate(result_text)

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

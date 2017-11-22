import multidict as multidict

import numpy as np
import time

import re
from PIL import Image
from os import path
from wordcloud import WordCloud

def getFrequencyDictForText(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    for text in sentence.split(" "):
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be",text):
            continue
        val = tmpDict.get(text,0)
        tmpDict[text.lower()] = val+1
    for key in tmpDict:
        fullTermsDict.add(key,tmpDict[key])
    return fullTermsDict



def makeImage(text):
    alice_mask = np.array(Image.open("alice_mask.png"))

    stopwords = {" "}

    wc = WordCloud(background_color="white", max_words=1000, mask=alice_mask,
                   stopwords=stopwords)
    # generate word cloud
    wc.generate_from_frequencies(text)

    # store to file
    filepath = 'wordcloud-{}.png'.format(round(time.time( ) *1000))

    wc.to_file(filepath)
    return filepath

d = path.dirname(__file__)

text = open(path.join(d, "what_is_tagcloud.txt")).read()
makeImage(getFrequencyDictForText(text))
import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
#import matplotlib.pyplot as plt

width = 800
height = 600
img = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(img)

with open("test.txt") as f:
    lines = f.readlines()
text = "".join(lines)
cv = CountVectorizer(min_df=0, charset_error="ignore")
counts = cv.fit_transform([text]).toarray().ravel()
words = np.array(cv.get_feature_names())
words = words[counts > 1]
counts = counts[counts > 1]
inds = np.argsort(counts)
counts = counts[inds]
words = words[inds]

for word, count in zip(words, counts):
    font_path = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
    img_array = np.array(img)
    found_place = False
    n_try = 0
    while not found_place:
        font = ImageFont.truetype(font_path, int(np.log(count)) * 20)
        orientation = random.choice([None, Image.ROTATE_90])
        transposed_font = ImageFont.TransposedFont(font,
                                                   orientation=orientation)
        draw.setfont(transposed_font)
        #draw.textsize gives size of word!
        size = draw.textsize(word)
        x = random.randint(0, width - size[0])
        y = random.randint(0, height - size[1])
        rect = img_array[y: y + size[1], x: x + size[0]]
        #draw.rectangle(((x, y), (x + size[0], y + size[1])))
        if rect.sum() == 0:
            break
        if n_try > 500:
            print("args")
            word = ""
            break
        n_try += 1
        #count -= 2
        #if count < 1:
            #break
    print(n_try)
    draw.text((x, y), word, fill=random.choice(['red', 'green', 'blue']))
    #img_array = np.array(img)
    #plt.matshow(img_array[y:y + size[1], x: x + size[0]].sum(axis=2))
    #plt.show()


img.show()

import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
#from scipy.ndimage import uniform_filter
#from scipy.misc import imsave


def make_wordcloud(words, counts, width=400, height=200):
    # sort words by counts
    inds = np.argsort(counts)[::-1]
    counts = counts[inds]
    words = words[inds]
    #words = words[:50]
    #counts = counts[:50]

    # create image
    img = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img)
    #i = 0
    for word, count in zip(words, counts):
        font_path = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
        img_array = np.asarray(img, dtype=np.float)
        #img_array = img_array.sum(axis=2)
        # set font size
        font_size = int(np.log(count)) * 20
        runs = 0
        integral = np.cumsum(np.cumsum(img_array, axis=0), axis=1)
        while True:
            font = ImageFont.truetype(font_path, font_size)
            # transpose font optionally
            orientation = random.choice([None, Image.ROTATE_90])
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            # get size of resulting text
            size = draw.textsize(word)
            # find possible places using convolution:
            off_x = size[0]
            off_y = size[1]
            mask2 = (integral[:-off_y, :-off_x]
                    + integral[off_y:, off_x:]
                    - integral[:-off_y, off_x:]
                    - integral[off_y:, :-off_x])
            mask2 = mask2 <= 0
            where = np.where(mask2)
            if len(where[0]):
                break
            font_size -= 1
            runs += 1
        idx = random.randint(0, len(where[0]) - 1)
        y, x = where[1][idx], where[0][idx]
        #draw.text((y, x), word,
                #fill=random.choice(['red', 'green', 'blue']))
        draw.text((y, x), word, fill="white")
        #imsave("img_%04d_mask2.png" % i, mask2)
        #imsave("img_%04d_mask.png" % i, mask)
        #imsave("img_%04d_integral.png" % i, integral)
        #img.save("img_%04d.png" % i)
        #i += 1

    img.show()

if __name__ == "__main__":
    with open("test.txt") as f:
        lines = f.readlines()
    text = "".join(lines)
    cv = CountVectorizer(min_df=0, charset_error="ignore")
    counts = cv.fit_transform([text]).toarray().ravel()
    words = np.array(cv.get_feature_names())
    words = words[counts > 1]
    counts = counts[counts > 1]
    make_wordcloud(words, counts, width=800, height=600)
    #make_wordcloud(words, counts, width=300, height=200)

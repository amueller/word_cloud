import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
from query_integral_image import query_integral_image


def make_wordcloud(words, counts, width=400, height=200):
    # sort words by counts
    inds = np.argsort(counts)[::-1]
    counts = counts[inds]
    words = words[inds]
    # create image
    img = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img)
    #i = 0
    integral = np.zeros((height, width), dtype=np.uint)
    img_array = np.asarray(img)
    for word, count in zip(words, counts):
        font_path = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
        #img_array = img_array.sum(axis=2)
        # set font size
        font_size = int(np.log(count)) * 20
        runs = 0
        while True:
            font = ImageFont.truetype(font_path, font_size)
            # transpose font optionally
            orientation = random.choice([None, Image.ROTATE_90])
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            # get size of resulting text
            size = draw.textsize(word)
            # find possible places using integral image:
            result = query_integral_image(integral, size[1], size[0])
            if result is not None:
                break
            # if we didn't find a place, make font smaller
            font_size -= 1
            runs += 1
        x, y = result
        draw.text((result[1], result[0]), word, fill="white")
        # recompute integral image
        img_array = np.asarray(img)
        # recompute bottom right
        partial_integral = np.cumsum(np.cumsum(img_array[x:, y:], axis=1),
                                     axis=0)
        # paste into old image
        # if x or y is zero it is a bit annoying
        if x > 0:
            if y > 0:
                partial_integral += (integral[x - 1, y:]
                                     - integral[x - 1, y - 1])
            else:
                partial_integral += integral[x - 1, y:]
        if y > 0:
            partial_integral += integral[x:, y - 1][:, np.newaxis]

        integral[x:, y:] = partial_integral

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
    make_wordcloud(words, counts, width=400, height=300)

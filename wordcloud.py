import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
from scipy.ndimage import uniform_filter


def make_wordcloud():
    width = 400
    height = 200
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
    inds = np.argsort(counts)[::-1]
    counts = counts[inds]
    words = words[inds]
    gridx, gridy = np.indices((height, width))
    #np.random.seed(5)
    #random.seed(0)
    num_words = 400
    words, counts = words[:num_words], counts[:num_words]

    for word, count in zip(words, counts):
        font_path = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
        img_array = np.array(img, dtype=np.float).sum(axis=2)
        # set font size
        font_size = int(np.log(count)) * 20
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
            mask = uniform_filter(img_array, size[::-1]) < 0.001
            # forbid border:
            mask[0: size[1] // 2] = False
            mask[-size[1] // 2:] = False
            mask[:, 0: size[0] // 2] = False
            mask[:, -size[0] // 2:] = False
            # get all available positions
            masked_y, masked_x = gridx[mask], gridy[mask]
            if len(masked_x):
                break
            font_size -= 1
        idx = np.random.randint(0, len(masked_x))
        x, y = masked_x[idx], masked_y[idx]
        x_offset = x - size[0] / 2
        y_offset = y - size[1] / 2
        draw.text((x_offset, y_offset), word,
                fill=random.choice(['red', 'green', 'blue']))

    img.show()

if __name__ == "__main__":
    make_wordcloud()

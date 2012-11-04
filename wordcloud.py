import Image
import ImageDraw
import ImageFont
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
from scipy.ndimage import uniform_filter
#import matplotlib.pyplot as plt
from scipy.misc import imsave

width = 400
height = 400
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

for word, count, i in zip(words[:50], counts[:50], range(50)):
    font_path = "/usr/share/fonts/truetype/droid/DroidSansMono.ttf"
    img_array = np.array(img, dtype=np.float).sum(axis=2)
    # set font size
    font = ImageFont.truetype(font_path, int(np.log(count)) * 20)
    #font = ImageFont.truetype(font_path, 30)
    # transpose font optionally
    #orientation = random.choice([None, Image.ROTATE_90])
    orientation = random.choice([None])
    transposed_font = ImageFont.TransposedFont(font,
                                               orientation=orientation)
    draw.setfont(transposed_font)
    # get size of resulting text
    size = draw.textsize(word)
    # find possible places using convolution:
    #mask = uniform_filter(img_array, size[::-1],
    #origin=[size[1]//2 - 1, size[0]//2 -1]) < 0.001
    mask = uniform_filter(img_array, size[::-1]) < 0.001
    # forbid border:
    mask[0: size[1] // 2] = False
    mask[-size[1] // 2:] = False
    mask[:, 0: size[0] // 2] = False
    mask[:, -size[0] // 2:] = False
    masked_y, masked_x = gridx[mask], gridy[mask]
    if not len(masked_x):
        break
    idx = np.random.randint(0, len(masked_x))
    x, y = masked_x[idx], masked_y[idx]
    x_offset = x - size[0] / 2
    y_offset = y - size[1] / 2
    draw.text((x_offset, y_offset), word,
            fill=random.choice(['red', 'green', 'blue']))
    #plt.matshow(mask)
    #plt.savefig("mask_%03d.png" % i)
    #plt.close()
    imsave("img_%03d_mask.png" % i, mask)
    mask = mask.astype(np.float)
    mask[y_offset: y_offset + size[1], x_offset: x_offset + size[0]] = .5
    mask[y, x] = 2
    imsave("img_%03d_mask2.png" % i, mask)
    img.save("img_%03d.png" % i)


img.show()

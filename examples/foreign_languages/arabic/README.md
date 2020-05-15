
A simple example for building a WordCloud from Arabic Text.

NOTE: Please note that this example requires:
- Two additional packages that should be installed separateley (arabic-reshaper and python-bidi)
- An Arabic Font file (see ./wordcloud/examples/foriegn_langauges/arabic/NotoNaskhArabic-unhinted) or download more fonts from: https://www.google.com/get/noto

This example is tested under:
- `Python 3.7.4`, macOS
- `arabic-reshaper==2.0.15` (https://pypi.org/project/python-bidi/)
- `python-bidi==0.4.2` (https://pypi.org/project/arabic-reshaper/)


```python
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -- Arabic text dependencies (Need to be installed separately)
from arabic_reshaper import reshape     # pip install arabic-reshaper
from bidi.algorithm import get_display  # pip install python-bidi

# -- The input text
my_arabic_text = "اللُّغَة العَرَبِيّة هي أكثرُ اللغاتِ السامية تحدثاً، وإحدى أكثر اللغات انتشاراً في العالم، يتحدثُها أكثرُ من 467 مليون نسمة"

# -- Generate word frequencies from `my_arabic_text`
from collections import Counter

COUNTS = Counter(my_arabic_text.split())

# -- Words orientation RTL
rtl = lambda w: get_display(reshape(f"{w}"))
counts = {rtl(k): v for k, v in COUNTS.most_common(10)}

# -- Get the Arabic font
import pathlib, os

THIS_DIR = pathlib.Path(__file__).parent.absolute()
font_file = "./fonts/NotoNaskhArabic-unhinted/NotoNaskhArabic-Regular.ttf"
font_file = os.path.join(THIS_DIR, font_file)

# -- Generate the word-cloud
wordcloud = WordCloud(font_path=font_file).generate_from_frequencies(counts)

# -- Display
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.savefig("arabic-wordcloud.png")
plt.show()
```

And the results:

![](arabic-wordcloud.png)
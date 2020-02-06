#!/usr/bin/env python
"""
Mix Fonts
=========

English, CJK, and emoji are mixed both across different words and
within each word. Fonts are aligned at their baselines.

"""
import os
import random

import emoji
import matplotlib.pyplot as plt
import regex as re
from fontTools.ttLib import TTFont

from wordcloud import MixedFontPattern
from wordcloud import WordCloud


def get_supported_chars(font_path):
    supported_chars = []
    with TTFont(font_path, 0, allowVID=0,
                ignoreDecompileErrors=True,
                fontNumber=-1) as ttf:
        for table in ttf["cmap"].tables:
            for glyph in list(table.cmap.items()):
                try:
                    char = chr(glyph[0])
                    supported_chars.append(char)
                except Exception:
                    continue
    return supported_chars


font_emoji = "fonts/Symbola/Symbola.ttf"
font_cjk = "fonts/SourceHanSerif/SourceHanSerifK-Light.otf"
font_paths = [
    MixedFontPattern(re.compile(pattern), path) for pattern, path in [
        (r"[\p{Emoji=Yes}\p{Emoji_Presentation=Yes}]+", font_emoji),
        (r"[\p{Han}\p{Katakana}\p{Hiragana}]+", font_cjk),
    ]
]

# construct word frequency dict.
wordfreq = {}
supported = get_supported_chars(font_emoji)
emojis = list(v for v in emoji.EMOJI_UNICODE.values() if v in supported)
wordfreq.update({random.choice(emojis): random.randint(10, 40)
                 for _ in range(200)})
wordfreq.update({
    emoji.emojize(word, use_aliases=True): n for word, n in {
        u"愛Myミィ": 75,
        u"I:beating_heart:紐育": 75,
        u"We:growing_heart:おんがく": 75,
        u"男": 90,
        u"女": 90,
        u":man_dancing:": 90,
        u":woman_dancing:": 90,
        u":couple_with_heart:": 90,
        u"愛": 90,
        u"love": 90,
        u"舞": 90,
        u"dance": 90,
        u":musical_note:": 90,
        u":musical_notes:": 90,
        u":musical_score:": 45,
    }.items()
})

wc = WordCloud(width=600,
               height=600,
               scale=1.5,
               relative_scaling=0.6,
               repeat=False,
               max_words=len(wordfreq),
               font_path=font_paths)
wc.generate_from_frequencies(wordfreq)

# generate an svg outout.
with open(os.path.splitext(os.path.basename(__file__))[0] + ".svg", 'w') as f:
    f.write(wc.to_svg(embed_font=True))

plt.figure(figsize=(8, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

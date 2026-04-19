#!/usr/bin/env python
"""
Create wordcloud with Arabic
===============
Generating a wordcloud from Arabic text

This example uses native WordCloud RTL support powered by Pillow+libraqm.
"""

from pathlib import Path

from wordcloud import WordCloud

# Support running from the repo or from a copied notebook context
HERE = Path(__file__).resolve().parent

ARABIC_TEXT = HERE / "arabicwords.txt"
NOTO_NASKH_ARABIC = HERE / "fonts" / "NotoNaskhArabic" / "NotoNaskhArabic-Regular.ttf"
# Fallback if Noto was removed (same bundle as ku_ckb_wordcloud.py)
ESTEDAD_FONT = HERE / "fonts" / "Estedad-v8.5" / "Estedad-Regular.ttf"


def pick_font():
    candidates = (
        NOTO_NASKH_ARABIC,
        ESTEDAD_FONT,
    )
    for path in candidates:
        if path.is_file():
            return str(path)
    return None


text = ARABIC_TEXT.read_text(encoding="utf-8")

font_path = pick_font()
if font_path is None:
    raise SystemExit(
        "No Arabic-capable font found under examples/fonts. "
        f"Expected Noto at {NOTO_NASKH_ARABIC}"
    )

# Generate a word cloud image
wordcloud = WordCloud(
    font_path=font_path,
    text_direction="auto",
    text_language="ar",
).generate(text)

# Export next to this script (matches README image path)
out = HERE / "arabic_example.png"
wordcloud.to_file(str(out))
print(f"Wrote {out}")

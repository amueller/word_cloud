#!/usr/bin/env python
"""
Kurdish word cloud - CKB (RTL) using Estedad from ./fonts/Estedad-v8.5.

No bidi pre-processing needed when Pillow has libraqm support.
"""

from pathlib import Path
from wordcloud import WordCloud

HERE = Path(__file__).resolve().parent

ESTEDAD_FONT = HERE / "fonts" / "Estedad-v8.5" / "Estedad-Regular.ttf"


def main() -> None:
    ku_path = HERE / "ku_ckb_wordcloud.txt"
    if not ku_path.is_file():
        raise SystemExit(f"Missing {ku_path}")

    text = ku_path.read_text(encoding="utf-8")

    if not ESTEDAD_FONT.is_file():
        raise SystemExit(f"Missing Estedad font at {ESTEDAD_FONT}")

    wc = WordCloud(
        font_path=str(ESTEDAD_FONT),
        width=1200,
        height=800,
        background_color="white",
        text_direction="auto",
        text_language="ar",
    ).generate(text)

    out = HERE / "ku_ckb_wordcloud.png"
    wc.to_file(str(out))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

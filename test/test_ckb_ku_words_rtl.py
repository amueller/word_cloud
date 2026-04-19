"""Tests for Kurdish Sorani (ckb) sample text and RTL WordCloud rendering."""

from pathlib import Path

import numpy as np
import pytest

import matplotlib

matplotlib.use("Agg")

from wordcloud import WordCloud

REPO_ROOT = Path(__file__).resolve().parents[1]
# Same file as examples/ku_ckb_wordcloud.py and the README Kurdish section
KU_CKB_SAMPLE_TEXT = REPO_ROOT / "examples" / "ku_ckb_wordcloud.txt"
ESTEDAD_FONT = (
    REPO_ROOT / "examples" / "fonts" / "Estedad-v8.5" / "Estedad-Regular.ttf"
)
NOTO_NASKH_ARABIC = (
    REPO_ROOT
    / "examples"
    / "fonts"
    / "NotoNaskhArabic"
    / "NotoNaskhArabic-Regular.ttf"
)

# Sorani Arabic-script words (strong bidi class AL); used if sample file is absent
_MINIMAL_KU_CKB_SAMPLE = "ئازادی کوردستان سلێمانی\n"


def _load_ku_sample_text() -> str:
    if KU_CKB_SAMPLE_TEXT.is_file():
        return KU_CKB_SAMPLE_TEXT.read_text(encoding="utf-8")
    return _MINIMAL_KU_CKB_SAMPLE


def _pick_rtl_font_path():
    """Prefer Estedad (Kurdish example); fall back to Noto Naskh Arabic."""
    for path in (ESTEDAD_FONT, NOTO_NASKH_ARABIC):
        if path.is_file():
            return path
    return None


@pytest.fixture
def ku_sample_text():
    return _load_ku_sample_text()


def test_ku_ckb_sample_includes_strong_rtl_letters(ku_sample_text):
    """Sorani Kurdish uses Arabic script; letters have bidi class AL (RTL)."""
    import unicodedata

    bidi_classes = {
        unicodedata.bidirectional(c) for c in ku_sample_text if not c.isspace()
    }
    assert "AL" in bidi_classes or "R" in bidi_classes, (
        "expected Arabic-letter or R bidi classes for Kurdish script text"
    )


def test_ku_ckb_wordcloud_generate_with_rtl_stack(ku_sample_text):
    """WordCloud renders CKB text with an Arabic-script font + Pillow/libraqm."""
    import PIL.features

    if not PIL.features.check("raqm"):
        pytest.skip("Pillow was built without libraqm (needed for RTL shaping)")

    font_path = _pick_rtl_font_path()
    if font_path is None:
        pytest.skip(
            "No bundled RTL font found (expected Estedad or Noto Naskh Arabic "
            "under examples/fonts/)"
        )

    wc = WordCloud(
        font_path=str(font_path),
        width=400,
        height=200,
        background_color="white",
        text_direction="auto",
        text_language="ar",
    )
    wc.generate(ku_sample_text)
    assert wc.words_

    arr = np.asarray(wc.to_array())
    assert arr.size > 0
    assert arr.std() > 0, "expected non-flat image after generate (words were drawn)"

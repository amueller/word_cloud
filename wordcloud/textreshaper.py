import arabic_reshaper
from bidi.algorithm import get_display


class TextReshaper(object):
    """
    TextReshaper class for reshaping text (Arabic or English or both)
    into a renderable format

     """
    @staticmethod
    def reshape(text):
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
        return text



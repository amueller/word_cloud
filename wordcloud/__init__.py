from .wordcloud import WordCloud, STOPWORDS, random_color_func, get_single_color_func
from .color_from_image import ImageColorGenerator
from pkg_resources import get_distribution

__version__ = get_distribution("wordcloud_cs489").version

__all__ = [
    "WordCloud",
    "STOPWORDS",
    "random_color_func",
    "get_single_color_func",
    "ImageColorGenerator",
    "__version__",
]

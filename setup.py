from setuptools import setup
from setuptools.extension import Extension

setup(
    ext_modules=[
        Extension(
            "wordcloud.query_integral_image", ["wordcloud/query_integral_image.c"]
        )
    ],
)

word cloud
==========

A little word cloud generator in Python.

Needs PIL and Cython (>= 0.16).

The example uses scikit-learn for extracting word counts from a text.
For scikit-learn <= 0.11, you have to remove the ``min_df`` keyword.

Build using ``python setup.py build_ext -i``.

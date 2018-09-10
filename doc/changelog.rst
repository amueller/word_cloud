.. _changelog:

=========
Changelog
=========

This is the list of changes to wordcloud between each release. For full
details, see the commit logs at https://github.com/amueller/word_cloud

WordCloud 1.5.0
===============

Examples
--------

* Add :ref:`sphx_glr_auto_examples_frequency.py` example for understanding how
  to generate a wordcloud using a dictionary of word frequency.
  Contributed by :user:`yoonsubKim`.

* Add :ref:`sphx_glr_auto_examples_wordcloud_cn.py` example.
  Contributed by :user:`FontTian` and improved by :user:`duohappy`.

Features
--------

* Add support for mask contour. Contributed by :user:`jsmedmar`.

  * Improve :ref:`wordcloud_cli` adding support for ``--contour_width``
    and ``--contour_color`` named arguments.

  * Improve :class:`wordcloud.WordCloud` API adding support for
    ``contour_width`` and ``contour_color`` keyword arguments.

  * Update :ref:`sphx_glr_auto_examples_masked.py` example.

* Update :class:`wordcloud.WordCloud` to support ``repeat`` keyword argument.
  If set to True, indicates whether to repeat words and phrases until ``max_words``
  or ``min_font_size`` is reached. Contributed by :user:`amueller`.

Wheels
------

* Support installation on Linux, macOS and Windows for Python 2.7, 3.4, 3.5, 3.6 and 3.7 by
  updating the Continuous Integration (CI) infrastructure and support the automatic creation
  and upload of wheels to `PyPI`_. Contributed by :user:`jcfr`.

  * Use `scikit-ci`_  to simplify and centralize the CI configuration. By having ``appveyor.yml``,
    ``.circleci/config.yml`` and ``.travis.yml`` calling the scikit-ci command-line executable,
    all the CI steps for all service are described in one `scikit-ci.yml`_ configuration file.

  * Use `scikit-ci-addons`_ to provide a set of scripts useful to help drive CI.

  * Simplify release process using `versioneer`_. Release process is now as simple as
    tagging a release, there is no need to manually update version in ``__init__.py``.

  * Remove use of miniconda and instead use `manylinux`_ docker images.

* Fix installation of the cli on all platforms leveraging `entry_points`_.
  See :issue:`420`. Contributed by :user:`jcfr`.

.. _manylinux: https://www.python.org/dev/peps/pep-0571/
.. _PyPI: https://pypi.org/project/wordcloud
.. _scikit-ci: http://scikit-ci.readthedocs.io
.. _scikit-ci-addons: http://scikit-ci-addons.readthedocs.io
.. _scikit-ci.yml: https://github.com/amueller/word_cloud/blob/master/scikit-ci.yml
.. _versioneer: https://github.com/warner/python-versioneer/
.. _entry_points: https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation

Bug fixes
---------

* :class:`wordcloud.WordCloud` API

  * Fix coloring with black image. Contributed by :user:`amueller`.

  * Improve error message when there is no space on canvas. Contributed by  :user:`amueller`.

* :ref:`wordcloud_cli`

  * Fix handling of invalid `regexp` parameter. Contributed by :user:`jcfr`.

Documentation
-------------

* Update :class:`wordcloud.WordCloud` ``color_func`` keyword argument documentation
  explaining how to create single color word cloud.
  Fix :issue:`185`. Contributed by :user:`maifeng`.

* Simplify and improve `README <https://github.com/amueller/word_cloud#readme>`_.
  Contributed by :user:`amueller`.

* Add :ref:`wordcloud_cli` document. Contributed by :user:`amueller`.

* Add :ref:`making_a_release` and :ref:`changelog` documents. Contributed by :user:`jcfr`.

* Improve sphinx gallery integration. Contributed by :user:`jcfr`.

Website
-------

* Setup automatic deployment of the website each time the `master` branch is updated.
  Contributed by :user:`jcfr`.

* Update `website <https://amueller.github.io/word_cloud>`_ to use `Read the Docs Sphinx Theme`.
  Contributed by :user:`amueller`.

Test
----

* Update testing infrastructure. Contributed by :user:`jcfr`.

  * Switch testing framework from nose to `pytest <https://docs.pytest.org>`_.

  * Enforce coding style by running `flake8 <http://flake8.pycqa.org/en/latest/index.html>`_
    each time a Pull Request is proposed or the `master` branch updated.

  * Support generating html coverage report locally running ``pytest``, ``coverage html`` and
    opening ``htmlcov/index.html`` document.


WordCloud 1.4.1
===============

Bug fixes
---------

* Improve stopwords list. Contributed by :user:`xuhdev`.


Test
----

* Remove outdated channel and use conda-forge. Contributed by :user:`amueller`.

* Add test for the command line utility. Contributed by :user:`xuhdev`.


WordCloud 1.4.0
===============

See https://github.com/amueller/word_cloud/compare/1.3.3...1.4


WordCloud 1.3.3
===============

See https://github.com/amueller/word_cloud/compare/1.3.2...1.3.3


WordCloud 1.3.2
===============

See https://github.com/amueller/word_cloud/compare/1.2.2...1.3.2


WordCloud 1.2.2
===============

See https://github.com/amueller/word_cloud/compare/1.2.1...1.2.2


WordCloud 1.2.1
===============

See https://github.com/amueller/word_cloud/compare/4c7ebf81...1.2.1
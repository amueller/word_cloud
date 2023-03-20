# Changelog

This is the list of changes to wordcloud between each release. For full
details, see the commit logs at <https://github.com/amueller/word_cloud>

<!--next-version-placeholder-->

## v1.8.4 (2023-03-20)

### Chore

- Replace versioneer with python-semantic-release ([`a486bbb`](https://github.com/Yuhao-C/word_cloud/commit/a486bbb9a03ec9e9d7eca88bd654aa1b5c1ca642))

## WordCloud 1.8.3

- Fix deprecated `numpy.int`.
- Fix styles.

## WordCloud 1.8.1

Release Date 11/11/2020

### Wheels

- Added wheels for Python 3.9.

## WordCloud 1.8.0

### Wheels

- Add support for building wheels for Python 3.8 for all platforms and
  32-bit wheels for windows **only**. See #547 and #549. Contributed
  by @amueller and @jcfr.

### Test

- Update CircleCI configuration to use
  [dockcross/manylinux1-x64](https://github.com/dockcross/dockcross#cross-compilers)
  image instead of obsolete [dockcross/manylinux-x64]{.title-ref} one.
  See #548. Contributed by @jcfr.

## WordCloud 1.7.0

### Features

- Add export of SVG files using `WordCloud.to_svg` by @jojolebarjos.
- Add missing options to the command line interface, [PR
  #527](https://github.com/amueller/word_cloud/pull/527) by
  @dm-logv.

### Bug fixes

- Make bigrams stopword aware, [PR
  #528](https://github.com/amueller/word_cloud/pull/529) by
  @carlgieringer.

## WordCloud 1.6.0

### Features

- Add support to render numbers and single letters using the
  `include_numbers` and `min_word_length` arguments.

### Examples

- Add `phx_glr_auto_examples_parrot.py` example showing another example of image-based coloring and masks.

## WordCloud 1.5.0

### Examples

- Add `sphx_glr_auto_examples_frequency.py` example for understanding how to generate a wordcloud using a dictionary of word frequency. Contributed by @yoonsubKim.
- Add `sphx_glr_auto_examples_wordcloud_cn.py` example. Contributed by @FontTian and improved by @duohappy.

### Features

- Add support for mask contour. Contributed by @jsmedmar.
  - Improve `wordcloud_cli` adding support for `--contour_width` and `--contour_color` named arguments.
  - Improve `wordcloud.WordCloud` API adding support for `contour_width` and `contour_color` keyword arguments.
  - Update `sphx_glr_auto_examples_masked.py` example.
- Update `wordcloud.WordCloud` to
  support `repeat` keyword argument. If set to True, indicates whether
  to repeat words and phrases until `max_words` or `min_font_size` is
  reached. Contributed by @amueller.

### Wheels

- Support installation on Linux, macOS and Windows for Python 2.7,
  3.4, 3.5, 3.6 and 3.7 by updating the Continuous Integration (CI)
  infrastructure and support the automatic creation and upload of
  wheels to [PyPI](https://pypi.org/project/wordcloud). Contributed by
  @jcfr`.
  - Use [scikit-ci](http://scikit-ci.readthedocs.io) to simplify and
    centralize the CI configuration. By having `appveyor.yml`,
    `.circleci/config.yml` and `.travis.yml` calling the scikit-ci
    command-line executable, all the CI steps for all service are
    described in one
    [scikit-ci.yml](https://github.com/amueller/word_cloud/blob/master/scikit-ci.yml)
    configuration file.
  - Use [scikit-ci-addons](http://scikit-ci-addons.readthedocs.io)
    to provide a set of scripts useful to help drive CI.
  - Simplify release process using
    [versioneer](https://github.com/warner/python-versioneer/).
    Release process is now as simple as tagging a release, there is
    no need to manually update version in `__init__.py`.
  - Remove use of miniconda and instead use
    [manylinux](https://www.python.org/dev/peps/pep-0571/) docker
    images.
- Fix installation of the cli on all platforms leveraging
  [entry_points](https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation).
  See #420. Contributed by @jcfr.

### Bug fixes

- `wordcloud.WordCloud` API
  - Fix coloring with black image. Contributed by
    @amueller.
  - Improve error message when there is no space on canvas.
    Contributed by @amueller.
- `wordcloud_cli`
  - Fix handling of invalid regexp parameter.
    Contributed by @jcfr.

### Documentation

- Update `wordcloud.WordCloud`
  `color_func` keyword argument documentation explaining how to create
  single color word cloud. Fix #185.
  Contributed by @maifeng.
- Simplify and improve
  [README](https://github.com/amueller/word_cloud#readme). Contributed
  by @amueller.
- Add `wordcloud_cli` document.
  Contributed by @amueller.
- Add `making_a_release` and
  `changelog` documents. Contributed by @jcfr.
- Improve sphinx gallery integration. Contributed by @jcfr.

### Website

- Setup automatic deployment of the website each time the
  master branch is updated. Contributed by
  @jcfr.
- Update [website](https://amueller.github.io/word_cloud) to use Read the Docs Sphinx Theme Contributed by @amueller.

### Test

- Update testing infrastructure. Contributed by
  @jcfr.
  - Switch testing framework from nose to
    [pytest](https://docs.pytest.org).
  - Enforce coding style by running
    [flake8](http://flake8.pycqa.org/en/latest/index.html) each time
    a Pull Request is proposed or the [master]{.title-ref} branch
    updated.
  - Support generating html coverage report locally running
    `pytest`, `coverage html` and opening `htmlcov/index.html`
    document.

## WordCloud 1.4.1

### Bug fixes

- Improve stopwords list. Contributed by @xuhdev.

### Test

- Remove outdated channel and use conda-forge. Contributed by
  @amueller.
- Add test for the command line utility. Contributed by
  @xuhdev.

## WordCloud 1.4.0

See <https://github.com/amueller/word_cloud/compare/1.3.3>\...1.4

## WordCloud 1.3.3

See <https://github.com/amueller/word_cloud/compare/1.3.2>\...1.3.3

## WordCloud 1.3.2

See <https://github.com/amueller/word_cloud/compare/1.2.2>\...1.3.2

## WordCloud 1.2.2

See <https://github.com/amueller/word_cloud/compare/1.2.1>\...1.2.2

## WordCloud 1.2.1

See <https://github.com/amueller/word_cloud/compare/4c7ebf81>\...1.2.1

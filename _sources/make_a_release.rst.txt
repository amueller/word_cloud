.. _making_a_release:

================
Making a release
================

This document guides a contributor through creating a release of the wordcloud
python packages.

A core developer should follow these steps to trigger the creation and upload of
a release `X.Y.Z` of **wordcloud** on `PyPI`_.

1. Make sure that all CI tests are passing: `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

2. In `doc/changelog.rst` change ``Next Release`` section header with
   ``WordCloud X.Y.Z`` and commit the changes using the same title::

    release=X.Y.Z
    git add doc/changelog.rst
    git commit -m "WordCloud $release"

3. Tag the release::

    release=X.Y.Z
    git tag --sign -m "WordCloud ${release}" ${release} master

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.

  .. note::

      We recommend using a GPG key to sign the tag.

4. Push the tag::

    git push origin ${release}

  .. note:: This will trigger builds on each CI services and automatically upload the wheels \
            and source distribution on `PyPI`_.

5. Check the status of the builds on `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

6. Once the builds are completed, check that the distributions are available on `PyPI`_.

7. Finally, make sure the package can be installed::

    mkvirtualenv test-install
    pip install wordcloud
    python -c "import wordcloud;print(wordcloud.__version__)"
    deactivate
    rmvirtualenv test-install

8. Add a ``Next Release`` section back in `doc/changelog.rst`, merge the result
   and push local changes.


.. _AppVeyor: https://ci.appveyor.com/project/amueller/word-cloud/history
.. _CircleCI: https://circleci.com/gh/amueller/word_cloud
.. _Travis CI: https://travis-ci.org/amueller/word_cloud/pull_requests

.. _PyPI: https://pypi.org/project/wordcloud
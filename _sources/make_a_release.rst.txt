================
Making a release
================

This document guides a contributor through creating a release of the wordcloud
python packages.

A core developer should follow these steps to trigger the creation and upload of
release packages of **wordcloud** on `PyPI`_.

1. Make sure that all CI tests are passing: `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

2. Tag the release. For version *X.Y.Z*::

    release=X.Y.Z
    git tag -s -m "wordcloud ${release}" ${release} origin/master

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.

3. Push the tag::

    git push origin ${release}

  .. note:: This will trigger builds on each CI services and automatically upload the wheels \
            and source distribution on `PyPI`_.

4. Check the status of the builds on `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

5. Once the builds are completed, check that the distributions are available on `PyPI`_.

6. Finally, make sure the package can be installed::

    mkvirtualenv test-install
    pip install wordcloud
    python -c "import wordcloud;print(wordcloud.__version__)"
    deactivate
    rmvirtualenv test-install


.. _AppVeyor: https://ci.appveyor.com/project/amueller/word-cloud/history
.. _CircleCI: https://circleci.com/gh/amueller/word_cloud
.. _Travis CI: https://travis-ci.org/amueller/word_cloud/pull_requests

.. _PyPI: https://pypi.org/project/wordcloud
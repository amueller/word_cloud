.. _making_a_release:

================
Making a release
================

This document guides a contributor through creating a release of the wordcloud
python packages.

A core developer should follow these steps to trigger the creation and upload of
a release `X.Y.Z` of **wordcloud** on `PyPI`_..

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

----------------------
Setting up environment
----------------------

1. First, `register for an account on PyPI <https://pypi.org>`_.


2. If not already the case, ask to be added as a ``Package Index Maintainer``.


3. Create a ``~/.pypirc`` file with your login credentials::

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    username=<your-username>
    password=<your-password>

    [pypitest]
    repository=https://test.pypi.org/legacy/
    username=<your-username>
    password=<your-password>

  where ``<your-username>`` and ``<your-password>`` correspond to your PyPI account.


---------------------
`PyPI`_: Step-by-step
---------------------

1. Make sure that all CI tests are passing: `AppVeyor`_, `CircleCI`_ and `Travis CI`_.


2. List all tags sorted by version

  .. code::

    $ git tag -l | sort -V


3. Choose the next release version number

  .. code::

    release=X.Y.Z

  .. warning::

    To ensure the packages are uploaded on `PyPI`_, tags must match this regular
    expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.


4. Download latest sources

  .. code::

    cd /tmp && git clone git@github.com:amueller/word_cloud && cd word_cloud


5. In `doc/changelog.rst` change ``Next Release`` section header with
   ``WordCloud X.Y.Z`` and commit the changes using the same title

  .. code::

    $ git add doc/changelog.rst
    $ git commit -m "WordCloud ${release}"


6. Tag the release

  .. code::

    $ git tag --sign -m "WordCloud ${release}" ${release} master

  .. note::

      We recommend using a GPG key to sign the tag.

7. Publish the tag

  .. code::

    $ git push origin ${release}

  .. note:: This will trigger builds on each CI services and automatically upload the wheels \
            and source distribution on `PyPI`_.

8. Check the status of the builds on `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

9. Once the builds are completed, check that the distributions are available on `PyPI`_.


10. Create a clean testing environment to test the installation

  .. code::

    $ mkvirtualenv wordcloud-${release}-install-test && \
      pip install wordcloud && \
      python -c "import wordcloud;print(wordcloud.__version__)"

  .. note::

      If the ``mkvirtualenv`` is not available, this means you do not have `virtualenvwrapper`_
      installed, in that case, you could either install it or directly use `virtualenv`_ or `venv`_.

11. Cleanup

  .. code::

    $ deactivate  && \
      rm -rf dist/* && \
      rmvirtualenv wordcloud-${release}-install-test


12. Add a ``Next Release`` section back in `doc/changelog.rst`, merge the result
    and push local changes::

    $ git push origin master


.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html

.. _AppVeyor: https://ci.appveyor.com/project/amueller/word-cloud/history
.. _CircleCI: https://circleci.com/gh/amueller/word_cloud
.. _Travis CI: https://travis-ci.org/amueller/word_cloud/pull_requests

.. _PyPI: https://pypi.org/project/wordcloud
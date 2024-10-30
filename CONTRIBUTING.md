# Contributing

To contribute to wordcloud, you'll need to follow the instructions in
[Creating a pull request from a fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).

In addition to the general procedure for creating a pull request, please follow
the following steps:

## Before starting development

### Use a correct version of Python

Python 3.7.x should be fine for development.

```
python --version
> Python 3.7.6
```

### Install all dependencies

```
pip install -U -r requirements.txt -r requirements-dev.txt
```

### Ensure that files are correctly formatted

```
flake8
```

### Ensure that tests pass

```
pip install -e .
pytest
```

## Before creating a pull request

### Confirm formatting and test passage

```
flake8
pytest
```

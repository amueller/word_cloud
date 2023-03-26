# Contributing

To contribute to wordcloud, you'll need to follow the instructions in [Creating a pull request from a fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).

In addition to the general procedure for creating a pull request, please follow the following steps:

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
pre-commit install
```

### Ensure that tests pass and files are correctly formatted

```
pre-commit run --all-files
```

## Before creating a pull request

### Commit changes

Again make sure that you have installed dependencies properly following the previous section.

When committing, tests and code style checks will run automatically.
You can successfully commit only if your changes pass the tests and style checks.
Otherwise, you will have to fix them before committing.

When writing the commit message, follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) specifications.
Commit messages that do not conform to the specifications will be rejected.

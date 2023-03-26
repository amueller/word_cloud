#!/usr/bin/env bash

set -e
set -o pipefail

PROG=$(basename $0)

BOT_USER_NAME=scikit-build-bot
BOT_USER_EMAIL=scikit-build-bot@scikit-build.org
TARGET_BRANCH=gh-pages

err() { echo -e >&2 ERROR: $@\\n; }
die() { err $@; exit 1; }

#-------------------------------------------------------------------------------
help() {
  cat >&2 <<ENDHELP
Usage: $PROG <ORG/NAME> <SOURCE_SHA> [--html-dir /path/to/html]

Publish directory to the $TARGET_BRANCH branch of a GitHub repository.

Arguments:
  <ORG/NAME>       repository slug where the files should be pushed.
  <SOURCE_SHA>     simple string referencing the repository from which
                   the files were generated.

Options:
  --html-dir       path to directory containing files to publish
                   (default: doc/_build/html).

Env. variables:
  GITHUB_TOKEN     this environment variable is expected to be set.


Example:

  GITHUB_TOKEN=xxxx $PROG amueller/word_cloud $(git rev-parse --short HEAD)


Notes:

  The username and email associated with the commit correspond to
  $BOT_USER_NAME and $BOT_USER_EMAIL.

ENDHELP
}

#-------------------------------------------------------------------------------
if [[ -z $GITHUB_TOKEN ]]; then
  err "skipping because GITHUB_TOKEN env. variable is not set"
  help
  exit 1
fi

if [[ $# -lt 2 ]]; then
  err "Missing org/name and source_sha parameters"
  help
  exit 1
fi

# Parse arguments
repo_slug=$1
source_sha=$2
shift 2

# Default values
html_dir=doc/_build/html

# Parse options
while [[ $# != 0 ]]; do
    case $1 in
        --html-dir)
            html_dir=$2
            shift 2
            ;;
        --help|-h)
            help
            exit 0
            ;;
        -*)
            err Unknown option \"$1\"
            help
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

echo "repo_slug [$repo_slug]"
echo "source_sha [$source_sha]"
echo "html_dir [$html_dir]"

#-------------------------------------------------------------------------------
cd $html_dir

# download current version
git clone git://github.com/$repo_slug -b $TARGET_BRANCH --depth 1 current_html

# ... and only keep associated history
mv current_html/.git .
rm -rf current_html

# add special file disabling Jekyll processing
touch .nojekyll

# configure git
pushURL=https://$GITHUB_TOKEN@github.com/$repo_slug
git config --add remote.origin.pushURL $pushURL
git config user.email $BOT_USER_EMAIL
git config user.name $BOT_USER_NAME

# commit
git add --all
git commit -m "Website update based of $repo_slug@${source_sha}

It was automatically generated and published using the script '${PROG}'

[ci skip]
"

# publish
git push origin HEAD:gh-pages


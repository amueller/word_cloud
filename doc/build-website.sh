#!/usr/bin/env bash

set -e
set -o pipefail

err() { echo -e >&2 ERROR: $@\\n; }
die() { err $@; exit 1; }

SCRIPT_DIR=$(cd $(dirname $0) || exit 1; pwd)

cd $SCRIPT_DIR/../

if [ ! -d .git ]; then
  die "Failed to locate the root of the current git-versioned project"
fi

SOURCE_SHA_REF=$(git rev-parse --short HEAD)

pushd doc
  pip install -r requirements-doc.txt
  make clean
  make html
  echo "sha:${SOURCE_SHA_REF}" >> _build/html/.buildinfo
popd


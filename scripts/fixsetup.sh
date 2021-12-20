#!/usr/bin/env bash
set -e

PYTHON_VERSIONS="${PYTHON_VERSIONS-3.7 3.8 3.9 3.10 3.11}"

for python_version in ${PYTHON_VERSIONS}; do
    rm -rf "__pypackages__/${python_version}/lib/mkdocstrings"
    rm -f "__pypackages__/${python_version}/lib/mkdocstrings.pth"
    rm -rf "__pypackages__/${python_version}/lib/mkdocs_autorefs"
    rm -f "__pypackages__/${python_version}/lib/mkdocs_autorefs.pth"
    cp -r ../mkdocstrings/src/mkdocstrings "__pypackages__/${python_version}/lib/"
    cp -r ../mkdocstrings-python/src/mkdocstrings/* "__pypackages__/${python_version}/lib/mkdocstrings"
    cp -r ../mkdocs-autorefs/src/mkdocs_autorefs "__pypackages__/${python_version}/lib/"
done
